import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest


SCRIPT = Path(os.environ.get(
    "RELEASE_AUTOMERGE_SCRIPT",
    Path(__file__).with_name("release-automerge.sh"),
))


class ReleaseAutomergeTest(unittest.TestCase):
    def run_automerge(self, approval_failures=0, merge_failures=0, state="OPEN", overrides=None, recovery=False):
        pull_request = {
            'state': 'OPEN' if state == 'AUTO_MERGE' else state,
            'author': {'login': 'app/github-actions'},
            'baseRefName': 'main',
            'headRefName': 'release-notes-example-abc123',
            'isCrossRepository': False,
            'autoMergeRequest': {} if state == 'AUTO_MERGE' else None,
            'labels': [{'name': 'release-notes-automerge'}],
            **(overrides or {}),
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            github = path / "gh"
            github.write_text("""#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import sys

path = Path(os.environ['MOCK_DIRECTORY'])
commands_file = path / 'commands.json'
commands = json.loads(commands_file.read_text()) if commands_file.exists() else []
arguments = sys.argv[1:]
commands.append({'arguments': arguments, 'token': os.environ.get('GH_TOKEN')})
commands_file.write_text(json.dumps(commands))
if arguments[:2] == ['pr', 'view']:
    result = subprocess.run(['jq', '-r', arguments[arguments.index('--jq') + 1]],
                            input=os.environ['MOCK_PULL_REQUEST'], text=True)
    sys.exit(result.returncode)
elif arguments[:2] == ['pr', 'list']:
    print('123')
    print('124')
elif arguments[:2] in (['pr', 'review'], ['pr', 'merge']):
    operation = arguments[1]
    calls = sum(command['arguments'] == arguments for command in commands)
    failures = 0 if '124' in arguments else int(os.environ['MOCK_' + operation.upper() + '_FAILURES'])
    if calls <= failures:
        print('502 Bad Gateway' if operation == 'review' else
              'GraphQL: Base branch was modified. Review and try the merge again.',
              file=sys.stderr)
        sys.exit(1)
""")
            github.chmod(0o755)
            sleep = path / "sleep"
            sleep.write_text("#!/bin/sh\nexit 0\n")
            sleep.chmod(0o755)
            environment = {
                **os.environ,
                "PATH": f"{path}:{os.environ['PATH']}",
                "MOCK_DIRECTORY": directory,
                "MOCK_PULL_REQUEST": json.dumps(pull_request),
                "MOCK_REVIEW_FAILURES": str(approval_failures),
                "MOCK_MERGE_FAILURES": str(merge_failures),
                "APPROVAL_TOKEN": "approval-token",
                "GH_TOKEN": "merge-token",
            }
            command = ["bash", str(SCRIPT), "123"]
            if recovery:
                workflow = Path(__file__).parents[1] / 'workflows/retry-release-automerge.yaml'
                run = workflow.read_text().split('        run: |\n', 1)[1].split('        env:', 1)[0]
                command = ['bash', '-e', '-c', textwrap.dedent(run)]
            result = subprocess.run(
                command, env=environment,
                cwd=Path(__file__).resolve().parents[2], capture_output=True, text=True,
            )
            commands_file = path / "commands.json"
            commands = json.loads(commands_file.read_text()) if commands_file.exists() else []
            return result, commands

    def test_should_approve_and_request_automerge(self):
        result, commands = self.run_automerge()
        self.assertEqual(0, result.returncode, result.stderr)
        review = next(command for command in commands if command['arguments'][:2] == ['pr', 'review'])
        merge = next(command for command in commands if command['arguments'][:2] == ['pr', 'merge'])
        self.assertEqual('approval-token', review['token'])
        self.assertEqual('merge-token', merge['token'])
        self.assertIn('--auto', merge['arguments'])
        self.assertNotIn('--admin', merge['arguments'])

    def test_should_recover_from_temporary_github_failures(self):
        for approval_failures, merge_failures in [(1, 0), (0, 2)]:
            with self.subTest(approval_failures=approval_failures, merge_failures=merge_failures):
                result, commands = self.run_automerge(approval_failures, merge_failures)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertTrue(any(command['arguments'][:2] == ['pr', 'merge'] for command in commands))

    def test_should_keep_failed_releases_for_later_followup(self):
        for approval_failures, merge_failures in [(10, 0), (0, 10)]:
            with self.subTest(approval_failures=approval_failures, merge_failures=merge_failures):
                result, commands = self.run_automerge(approval_failures, merge_failures)
                self.assertNotEqual(0, result.returncode)
                self.assertFalse(any('--remove-label' in command['arguments'] for command in commands))
                failed_operation = 'review' if approval_failures else 'merge'
                attempts = sum(command['arguments'][:2] == ['pr', failed_operation] for command in commands)
                self.assertEqual(5, attempts)

    def test_should_follow_up_other_releases_when_one_fails(self):
        result, commands = self.run_automerge(approval_failures=10, recovery=True)
        self.assertNotEqual(0, result.returncode)
        listing = next(command for command in commands if command['arguments'][:2] == ['pr', 'list'])
        self.assertIn('release-notes-automerge', listing['arguments'])
        self.assertTrue(any(command['arguments'][:2] == ['pr', 'merge'] and '124' in command['arguments'] for command in commands))
        self.assertFalse(any(command['arguments'][:2] == ['pr', 'merge'] and '123' in command['arguments'] for command in commands))

    def test_should_leave_active_automerge_to_github(self):
        result, commands = self.run_automerge(state='AUTO_MERGE')
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(any(command['arguments'][:2] in (['pr', 'review'], ['pr', 'merge']) for command in commands))

    def test_should_reject_unexpected_pull_requests(self):
        for overrides in [
            {'author': {'login': 'contributor'}},
            {'baseRefName': 'another-branch'},
            {'headRefName': 'feature-branch'},
            {'isCrossRepository': True},
            {'labels': []},
        ]:
            with self.subTest(overrides=overrides):
                result, commands = self.run_automerge(overrides=overrides)
                self.assertNotEqual(0, result.returncode)
                self.assertFalse(any(command['arguments'][:2] in (['pr', 'review'], ['pr', 'merge']) for command in commands))


if __name__ == '__main__':
    unittest.main()
