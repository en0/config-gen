from keystore_ini import KeystoreIni


def Keystore(ks_type=None, **kwargs):
    _type = ks_type or "ini"

    if _type.lower() == "ini":
        return KeystoreIni(**kwargs)
    else:
        raise ValueError("Unkonwn type: {}".format(ks_type))
