import logging
import typing

log = logging.getLogger(__name__)


class EnvConfig:
    envname: str
    domain: str
    no_dotapi: typing.List[str] = ["auth"]

    # this same dict is inherited (and therefore shared!) by all subclasses
    _registry: typing.Dict[str, typing.Type["EnvConfig"]] = {}

    # this is an easier hook to use than metaclass definition -- register every subclass
    # in this dict automatically
    #
    # as a result, anyone can define
    #
    #       class BetaEnv(EnvConfig):
    #           domain = "beta.foo.bar.example.com"
    #           envname = "beta"
    #
    # and retrieve it with get_config_by_name("beta")
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry[cls.envname] = cls

    @classmethod
    def get_service_url(cls, service):
        # you can override any name with a config attribute
        service_url_attr = f"{service}_url"
        if hasattr(cls, service_url_attr):
            return getattr(cls, service_url_attr)

        # the typical pattern for a service hostname is X.api.Y
        # X=transfer, Y=preview.globus.org => transfer.api.preview.globus.org
        # check `no_dotapi` for services which don't have `.api` in their names
        if service in cls.no_dotapi:
            return f"https://{service}.{cls.domain}/"
        return f"https://{service}.api.{cls.domain}/"

    @classmethod
    def get_by_name(cls, envname: str) -> typing.Optional[typing.Type["EnvConfig"]]:
        return cls._registry.get(envname)


def get_service_url(environment, service):
    log.debug(f'Service URL Lookup for "{service}" under env "{environment}"')
    conf = EnvConfig.get_by_name(environment)
    if not conf:
        raise ValueError(f'Unrecognized environment "{environment}"')
    url = conf.get_service_url(service)
    log.debug(f'Service URL Lookup Result: "{service}" is at "{url}"')
    return url


#
# public environments
#


class ProductionEnvConfig(EnvConfig):
    envname = "production"
    domain = "globus.org"
    nexus_url = "https://nexus.api.globusonline.org/"


class PreviewEnvConfig(EnvConfig):
    envname = "preview"
    domain = "preview.globus.org"


#
# environments for internal use only
#
for envname in ["sandbox", "integration", "test", "staging"]:
    # use `type()` rather than the `class` syntax to control classnames
    type(
        f"{envname.title()}EnvConfig",
        (EnvConfig,),
        {"envname": envname, "domain": f"{envname}.globuscs.info"},
    )
