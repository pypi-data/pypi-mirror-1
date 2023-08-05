import warnings

def chipmunk_body_anims(*pargs, **kwargs):
    warnings.warn("rabbyt.physics.chipmunk_body_anims has been moved to "
            "rabbyt.chipmunkglue.chipmunk_body_anims.  Please import it from "
            "there.  (rabbyt.physics is going bye-bye.)", stacklevel=2)
    from rabbyt.chipmunkglue import chipmunk_body_anims
    return chipmunk_body_anims(*pargs, **kwargs)
