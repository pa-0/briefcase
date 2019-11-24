from briefcase.config import BaseConfig
from briefcase.exceptions import BriefcaseCommandError

from .base import BaseCommand


class PublishCommand(BaseCommand):
    @property
    def publication_channels(self):
        "The list of publication channel backends that are available for this format"
        return ['s3']

    @property
    def default_publication_channel(self):
        "The default publication channel for this format"
        return 's3'

    def add_options(self, parser):
        parser.add_argument(
            '-c',
            '--channel',
            choices=self.publication_channels,
            default=self.default_publication_channel,
            help='The channel to publish to'
        )

    def publish_app(self, app: BaseConfig, channel: str):
        """
        Publish an application.

        :param app: The application to publish
        :param str: The publication channel to use
        """
        print("TODO: Publish {app.name} to {channel}".format(
            app=app,
            channel=channel,
        ))

    def __call__(self):
        self.verify_tools()

        # Check the apps have been built first.
        for app_name, app in self.apps.items():
            binary_file = self.binary_path(app)
            if not binary_file.exists():
                raise BriefcaseCommandError(
                    "Application {app_name} has not been built. "
                    "Build (and test!) the app before publishing.".format(
                        app_name=app_name
                    )
                )

        # Then publish them all to the selected channel.
        for app_name, app in sorted(self.apps.items()):
            self.publish_app(app, channel=self.options.channel)
