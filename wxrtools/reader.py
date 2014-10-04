import subprocess
from tempfile import TemporaryFile

def preprocess_wxr_file(fname):
    # Not proud of this one, but I haven't dared to dig into the xmllint
    # sources yet. A lxml implementation would probably make sense, both
    # to spare IO and not having to fork...
    out = TemporaryFile()
    with TemporaryFile() as err:
        if subprocess.call(("xmllint", "--nonet", "--recover", fname),
                           stdout=out, stderr=err, close_fds=False) != 0:
            # Handle files so broken even xmllint --recover cant handle them.
            return err
            # err.seek(0)
            # for line in err:
            #     print

    out.seek(0)
    return out

def wxr_open(fname):
    return preprocess_wxr_file(fname)


