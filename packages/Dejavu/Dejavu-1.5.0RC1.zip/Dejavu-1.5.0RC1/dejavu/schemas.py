
from dejavu import errors, units


__all__ = ['DeployedVersion', 'Schema',
           ]


class DeployedVersion(units.Unit):
    """Which schema version the current deployment has reached."""
    ID = units.UnitProperty(unicode)
    Version = units.UnitProperty(int)
    sequencer = units.UnitSequencer()


class Schema(object):
    """Schema versioning tool for Dejavu Units.
    
    Make a subclass of this base class to manage changes to your model layer
    (Units and UnitProperties) as your application grows. Each time you make
    a change to your model, add a new upgrade_to_X method to your subclass,
    and increment the "latest" attribute to match:
    
    class MySchema(dejavu.Schema):
        
        latest = 1
        
        def upgrade_to_1(self):
            # Remove Employee.ZipCode and add .StartDate
            self.arena.drop_property(Employee, "ZipCode")
            self.arena.add_property(Employee, "StartDate")
    
    Then, in your deployment scripts, you can choose how much you want to
    automate control of the schema.
    
        schema = MySchema(myarena)
        
        if cmd == 'upgrade':
            schema.upgrade()
        elif cmd == 'install':
            schema.assert_storage()
        else:
            schema.assert_version()
    """
    
    guid = ""
    latest = 0
    stage = None
    
    def __init__(self, arena):
        # Since schema upgrades may take some time, we keep track of our
        # own processing state. Legal values are:
        #   None              = not working on an upgrade
        #   0 to self.latest  = working on an upgrade to this version
        self.stage = None
        
        self.arena = arena
        arena.register(DeployedVersion)
        self._deployed_unit = None
    
    def deployed_unit(self, default=None):
        """Retrieve our DeployedVersion unit, optionally creating it."""
        if not self.arena.has_storage(DeployedVersion):
            self.arena.create_storage(DeployedVersion)
        
        if self._deployed_unit is None:
            box = self.arena.new_sandbox()
            try:
                du = box.unit(DeployedVersion, ID=self.guid)
                if du is None:
                    if default is None:
                        raise errors.DejavuError("Missing DeployedVersion unit.")
                    else:
                        du = DeployedVersion(ID=self.guid, Version=default)
                        box.memorize(du)
                self._deployed_unit = du
            finally:
                box.flush_all()
        return self._deployed_unit
    
    def versioned(self):
        """Return True if this installation has a DeployedVersion, false otherwise."""
        box = self.arena.new_sandbox()
        try:
            return bool(box.unit(DeployedVersion, ID=self.guid))
        finally:
            box.flush_all()
    
    def _get_dep(self):
        # Note that we default the Version to latest.
        # This allows new installs to skip all the upgrade steps,
        # and just use the latest class definitions when they call
        # assert_storage. However, it means that if you deploy your
        # apps for a while without a Schema, and then introduce one
        # later, you must manually decrement DeployedVersion from
        # "latest" to the actual deployed version *before* running
        # your app for the first time (or things will break due to
        # the difference between the latest and deployed schema).
        return self.deployed_unit(self.latest).Version
    
    def _set_dep(self, newvalue):
        depunit = self.deployed_unit(newvalue)
        depunit.Version = newvalue
        # Skip the sandbox, so we can save without repress
        self.arena.storage(DeployedVersion).save(depunit, forceSave=True)
    
    deployed = property(_get_dep, _set_dep, doc="Deployed version")
    
    def upgrade(self, version=None):
        """Upgrade deployment to version arg [latest]. Idempotent."""
        if version is None:
            version = self.latest
        
        # Run upgrade_to_X methods.
        if self.deployed > version:
            raise errors.DejavuError("Deployed version is greater than latest version.")
        for step in range(self.deployed, version):
            self.stage = step
            procedure = getattr(self, "upgrade_to_%s" % (step + 1), None)
            if procedure:
                procedure()
            self.deployed = step + 1
        
        self.stage = None
    
    def upgrade_to_0(self):
        pass
    
    def assert_storage(self):
        """Assert that each class has storage reserved for it.
        
        You may choose to call this method in an admin script (at the
        discretion of the deployer), or on application startup. If you
        call this method on every application start, you should do it
        after calling upgrade(). Once all of the upgrade methods are done,
        you can then safely use this method to assert the _final_ schemas
        for all classes. Note that, if the DeployedVersion unit was just
        created (our actual deployed version was unknown), then some of
        the upgrade methods may fail. However, they could fail just as
        easily if you run assert_storage before the upgrade methods.
        """
        
        classes = self.arena._registered_classes.keys()
        if DeployedVersion in classes:
            classes.remove(DeployedVersion)
        
        for cls in classes:
            if not self.arena.has_storage(cls):
                self.arena.create_storage(cls)
    
    def assert_version(self):
        """Die if schema version is missing or out of sync."""
        msg = None
        if not self.versioned:
            msg = ("This application now uses a versioned schema, but the "
                   "installed version could not be determined. You must "
                   "either install the application or manually set the "
                   "version number.")
        if self.deployed > self.latest:
            msg = "Deployed version is greater than the latest version!?!"
        if self.deployed < self.latest:
            msg = ("Deployed version is less than the latest version. "
                   "You must upgrade before proceeding.")
        if msg:
            raise errors.DejavuError(msg)

