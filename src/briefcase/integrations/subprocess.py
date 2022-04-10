import logging
import shlex
import subprocess

logger = logging.getLogger(__name__)


class Subprocess:
    """
    A wrapper around subprocess that can be used as a logging point for
    commands that are executed.
    """
    def __init__(self, command):
        self.command = command
        self._subprocess = subprocess

    def prepare(self):
        """
        Perform any environment preparation required to execute processes.
        """
        # This is a no-op; the native subprocess environment is ready-to-use.
        pass

    def final_kwargs(self, **kwargs):
        """Convert subprocess keyword arguments into their final form.
        """
        # If `env` has been provided, inject a full copy of the local
        # environment, with the values in `env` overriding the local
        # environment.
        try:
            extra_env = kwargs.pop('env')
            kwargs['env'] = self.command.os.environ.copy()
            kwargs['env'].update(extra_env)
        except KeyError:
            # No explicit environment provided.
            pass

        # If `cwd` has been provided, ensure it is in string form.
        try:
            cwd = kwargs.pop('cwd')
            kwargs['cwd'] = str(cwd)
        except KeyError:
            pass

        return kwargs

    def run(self, args, **kwargs):
        """A wrapper for subprocess.run()

        If verbosity >= 2, the executed command will be printed to the console.

        The behavior of this method is identical to subprocess.run(),
        except for the `env` argument. If provided, the current system
        environment will be copied, and the contents of env overwritten
        into that environment.
        """
        # Invoke subprocess.run().
        # Pass through all arguments as-is.
        # All exceptions are propagated back to the caller.
        self._log_command(args)
        self._log_environment(kwargs.get("env"))

        logger.debug("Command Output:")
        ret = self._subprocess.run(
            [
                str(arg) for arg in args
            ],
            **self.final_kwargs(**kwargs)
        )

        self._log_return_code(ret.returncode)
        return ret

    def check_output(self, args, **kwargs):
        """A wrapper for subprocess.check_output()

        If verbosity >= 2, the executed command will be printed to the console.

        The behavior of this method is identical to subprocess.check_output(),
        except for the `env` argument. If provided, the current system
        environment will be copied, and the contents of env overwritten
        into that environment.
        """
        self._log_command(args)
        self._log_environment(kwargs.get("env"))

        ret = self._subprocess.check_output(
            [
                str(arg) for arg in args
            ],
            **self.final_kwargs(**kwargs)
        )

        self._log_output(ret)
        return ret

    def Popen(self, args, **kwargs):
        """A wrapper for subprocess.Popen()

        If verbosity >= 2, the executed command will be printed to the console.

        The behavior of this method is identical to subprocess.Popen(),
        except for the `env` argument. If provided, the current system
        environment will be copied, and the contents of env overwritten
        into that environment.
        """
        self._log_command(args)
        self._log_environment(kwargs.get("env"))

        return self._subprocess.Popen(
            [
                str(arg) for arg in args
            ],
            **self.final_kwargs(**kwargs)
        )

    @staticmethod
    def _log_command(args):
        """
        Log the entire console command being executed.
        """
        logger.debug("")
        logger.debug("Running Command:")
        logger.debug("\t{cmdline}".format(
            cmdline=' '.join(shlex.quote(str(arg)) for arg in args)
        ))

    def _log_environment(self, env=None):
        """
        Log the state of environment variables prior to command execution.
        """
        if not logger.isEnabledFor(logging.DEBUG):
            return
        # use merged environment if it exists, else current environment
        env = env or self.command.os.environ
        logger.debug("Environment:")
        for env_var, value in env.items():
            logger.debug("\t{env_var}={value}".format(env_var=env_var, value=value))

    @staticmethod
    def _log_output(output):
        """
        Log the output of the executed command.
        """
        if output:
            logger.debug("Command Output:")
            for line in str(output).splitlines():
                logger.debug("\t{line}".format(line=line))

    @staticmethod
    def _log_return_code(return_code):
        """
        Log the output value of the executed command.
        """
        logger.debug("Return code: {return_code}".format(return_code=return_code))
