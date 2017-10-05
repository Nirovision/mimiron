# -*- coding: utf-8 -*-
import string
import random

from mimiron.vendor.git_extensions.parsers import parse_commit_message


class TestGitExtensionsCommitParserV1(object):
    def test_empty_commit(self):
        message = ''
        expected_output = None

        assert parse_commit_message(message) == expected_output

    def test_random_commit_message(self):
        for _ in xrange(random.randint(10, 20)):
            pool = list(string.printable)
            random.shuffle(pool)
            message = ''.join(pool)[:random.randint(0, len(string.printable))]

            expected_output = None
            assert parse_commit_message(message) == expected_output

    def test_empty_message_body(self):
        service_name = 'example-service'
        tag = '0b5fb3e5-c91d-45f1-8c6e-5ceeaa11ec8f'
        env = 'test-environment'

        message = 'chore(tfvars): bump %s#%s "%s"' % (service_name, tag, env,)
        expected_output = None

        assert parse_commit_message(message) == expected_output

    def test_message_with_committed_by(self):
        author_name = 'David Vuong'
        author_email = 'david@imageintelligence.com'
        service_name = 'example-service'
        tag = '0b5fb3e5-c91d-45f1-8c6e-5ceeaa11ec8f'
        env = 'test-environment'

        message = '\n'.join([
            'chore(tfvars): bump %s#%s "%s"' % (service_name, tag, env,),
            '\n'
            'committed-by: %s <%s>' % (author_name, author_email,),
        ])
        expected_output = {
            'author_name': author_name,
            'author_email': author_email,
        }
        assert parse_commit_message(message) == expected_output

    def test_message_with_committed_by_no_email(self):
        author_name = 'David Vuong'
        author_email = None
        service_name = 'example-service'
        tag = '0b5fb3e5-c91d-45f1-8c6e-5ceeaa11ec8f'
        env = 'test-environment'

        message = '\n'.join([
            'chore(tfvars): bump %s#%s "%s"' % (service_name, tag, env,),
            '\n'
            'committed-by: %s' % (author_name,),
        ])
        expected_output = {
            'author_name': author_name,
            'author_email': author_email,
        }
        assert parse_commit_message(message) == expected_output

    # def test_all_bump_commit_attributes_available(self):
    #     version = '0.0.1'
    #     author_name = 'David Vuong'
    #     author_email = 'david@imageintelligence.com'
    #     service_name = 'example-service'
    #     tag = '0b5fb3e5-c91d-45f1-8c6e-5ceeaa11ec8f'
    #     env = 'test-environment'
    #
    #     message = '\n'.join([
    #         'chore(tfvars): bump %s#%s "%s"' % (service_name, tag, env),
    #         '\n'
    #         'committed-by: %s <%s>' % (author_name, author_email),
    #         'service-name: %s' % service_name,
    #         'service-tag: %s' % tag,
    #         'environment: %s' % env,
    #         '\n'
    #         'Committed via Mimiron v%s (https://github.com/ImageIntelligence/mimiron)' % version
    #     ])
    #     expected_output = {
    #         'version': version,
    #         'author_name': author_name,
    #         'author_email': author_email,
    #         'service_name': service_name,
    #         'tag': tag,
    #         'environment': env,
    #     }
    #     assert parse_commit_message(message) == expected_output
