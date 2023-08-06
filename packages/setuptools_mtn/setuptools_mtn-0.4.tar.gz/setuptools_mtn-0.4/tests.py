from StringIO import StringIO
import os.path

import setuptools_mtn

# This class used to have more to it, I promise.
class Inventory (object):
    def __init__(self, full):
        self.full = full

INVENTORIES = {
    # From Monotone 0.32
    4: Inventory(
"""  P 0 0 base_changing_content
  M 0 0 base_disappearing_content
 AP 0 0 base_new_content
D   0 0 base_removed_content
 R  0 1 base_renamed_content
R   1 0 base_renaming_content
    0 0 prefix/
    0 0 prefix/content
    0 0 prefixtrick/
    0 0 prefixtrick/content
    0 0 subdir1/
  P 0 0 subdir1/sub1_changing_content
  M 0 0 subdir1/sub1_disappearing_content
 AP 0 0 subdir1/sub1_new_content
D   0 0 subdir1/sub1_removed_content
 R  0 2 subdir1/sub1_renamed_content
R   2 0 subdir1/sub1_renaming_content
 AP 0 0 subdir2/
 AP 0 0 subdir2/sub2_changing_content
 AP 0 0 subdir2/sub2_disappearing_content
 AP 0 0 subdir2/sub2_removed_content
 AP 0 0 subdir2/sub2_renaming_content
  U 0 0 unknown_file
  U 0 0 unknown_subdir/
  U 0 0 unknown_subdir/unknown_subdir_file
"""),

    # From Monotone 0.36
    5: Inventory(
"""  P 0 0 base_changing_content
  M 0 0 base_disappearing_content
 AP 0 0 base_new_content
D   0 0 base_removed_content
 R  0 1 base_renamed_content
R   1 0 base_renaming_content
    0 0 prefix/
    0 0 prefix/content
    0 0 prefixtrick/
    0 0 prefixtrick/content
    0 0 subdir1/
  P 0 0 subdir1/sub1_changing_content
  M 0 0 subdir1/sub1_disappearing_content
 AP 0 0 subdir1/sub1_new_content
D   0 0 subdir1/sub1_removed_content
 R  0 2 subdir1/sub1_renamed_content
R   2 0 subdir1/sub1_renaming_content
 AP 0 0 subdir2/
 AP 0 0 subdir2/sub2_changing_content
 AP 0 0 subdir2/sub2_disappearing_content
 AP 0 0 subdir2/sub2_removed_content
 AP 0 0 subdir2/sub2_renaming_content
  U 0 0 unknown_file
  U 0 0 unknown_subdir/
"""),

    # From Monotone 0.37
    6: Inventory(
"""    path ""
old_type "directory"
new_type "directory"
 fs_type "directory"
  status "known"

    path "base_changing_content"
old_type "file"
new_type "file"
 fs_type "file"
  status "known"
 changes "content"

    path "base_disappearing_content"
old_type "file"
new_type "file"
 fs_type "none"
  status "missing"

    path "base_new_content"
new_type "file"
 fs_type "file"
  status "added" "known"
 changes "content"

    path "base_removed_content"
old_type "file"
 fs_type "none"
  status "dropped"

    path "base_renamed_content"
new_type "file"
old_path "base_renaming_content"
 fs_type "file"
  status "rename_target" "known"

    path "base_renaming_content"
old_type "file"
new_path "base_renamed_content"
 fs_type "none"
  status "rename_source"

    path "prefix"
old_type "directory"
new_type "directory"
 fs_type "directory"
  status "known"

    path "prefix/content"
old_type "file"
new_type "file"
 fs_type "file"
  status "known"

    path "prefixtrick"
old_type "directory"
new_type "directory"
 fs_type "directory"
  status "known"

    path "prefixtrick/content"
old_type "file"
new_type "file"
 fs_type "file"
  status "known"

    path "subdir1"
old_type "directory"
new_type "directory"
 fs_type "directory"
  status "known"

    path "subdir1/sub1_changing_content"
old_type "file"
new_type "file"
 fs_type "file"
  status "known"
 changes "content"

    path "subdir1/sub1_disappearing_content"
old_type "file"
new_type "file"
 fs_type "none"
  status "missing"

    path "subdir1/sub1_new_content"
new_type "file"
 fs_type "file"
  status "added" "known"
 changes "content"

    path "subdir1/sub1_removed_content"
old_type "file"
 fs_type "none"
  status "dropped"

    path "subdir1/sub1_renamed_content"
new_type "file"
old_path "subdir1/sub1_renaming_content"
 fs_type "file"
  status "rename_target" "known"

    path "subdir1/sub1_renaming_content"
old_type "file"
new_path "subdir1/sub1_renamed_content"
 fs_type "none"
  status "rename_source"

    path "subdir2"
new_type "directory"
 fs_type "directory"
  status "added" "known"

    path "subdir2/sub2_changing_content"
new_type "file"
 fs_type "file"
  status "added" "known"
 changes "content"

    path "subdir2/sub2_disappearing_content"
new_type "file"
 fs_type "file"
  status "added" "known"
 changes "content"

    path "subdir2/sub2_removed_content"
new_type "file"
 fs_type "file"
  status "added" "known"
 changes "content"

    path "subdir2/sub2_renaming_content"
new_type "file"
 fs_type "file"
  status "added" "known"
 changes "content"

   path "unknown_file"
fs_type "file"
 status "unknown"

   path "unknown_subdir"
fs_type "directory"
 status "unknown"

   path "unknown_subdir/unknown_subdir_file"
fs_type "file"
 status "unknown"
"""),
    }
# v6 and v7 (Monotone 0.39) seem to be the same.
INVENTORIES[7] = INVENTORIES[6]

# Note: I've chosen not to return missing (from Monotone's
# perspective) files from this plug-in.  Rationale: setuptools wants
# to include files.  Why try to tell it to include files that aren't
# there?

ALL_EXPECTED_FILES = set((
    "base_changing_content",
    "base_new_content",
    "base_renamed_content",
    "prefix",
    "prefixtrick", 
    "prefixtrick/content",
    "subdir1",
    "subdir2",
    "subdir2/sub2_changing_content",
    "subdir2/sub2_disappearing_content",
    "subdir2/sub2_removed_content",
    "subdir2/sub2_renaming_content",
    ))

SUBDIR_EXPECTED_FILES = set((
    "subdir1/sub1_changing_content",
    "subdir1/sub1_new_content",
    "subdir1/sub1_renamed_content",
    ))
ALL_EXPECTED_FILES.update(SUBDIR_EXPECTED_FILES)

PREFIX_EXPECTED_FILES = set((
    "prefix/content",
    ))
ALL_EXPECTED_FILES.update(PREFIX_EXPECTED_FILES)

class MockMonotone (StringIO):
    """Looks like a file with an extra method or two."""
    def __init__(self, content="", exit_status=0):
        StringIO.__init__(self, content)
        self.exit_status = exit_status
        self._closed = False

    def close(self):
        assert not self._closed, "already closed"
        self._closed = True
        return self.exit_status == 0

class MockMonotoneFactory (object):
    # XXX This is a poorly named class, I think.
    def __init__(self, interface_version, inventory):
        self.version = interface_version
        self.inventory = inventory
        self.root = "/mtn/root"
        self.cwd = "/some/other/dir"

    def mock_call_with_cwd(self, path, func, *args, **kwargs):
        saved_cwd = self.cwd
        self.cwd = path
        try:
            return func(*args, **kwargs)
        finally:
            self.cwd = saved_cwd

    def mock_automate_monotone(self, command, capture_stderr=False):
        if command == "interface_version":
            assert capture_stderr
            return MockMonotone("%.1f" % (self.version,))
        elif command == "inventory":
            assert not capture_stderr
            assert os.path.commonprefix((self.root, self.cwd)) == self.root
            return MockMonotone(self.inventory.full)
        assert False, "unknown command: %s" % (command,)

    def find_files_in_mtn(self, rel_path):
        assert not os.path.isabs(rel_path), `a_path`
        mtn_root = self.root
        abs_path = os.path.normpath(os.path.join(mtn_root, rel_path))
        return list(setuptools_mtn.filter_inventory(rel_path, abs_path,
                                                    mtn_root))

class TestSetuptoolsMtn (object):
    def setUp(self):
        self.mocked = dict( (name, getattr(setuptools_mtn, name))
                            for name in ("automate_monotone",
                                         "call_with_cwd",
                                         ) )
        self.versions = iter(sorted(INVENTORIES))

    def tearDown(self):
        for name, original_value in self.mocked.iteritems():
            setattr(setuptools_mtn, name, original_value)

    def mock_for_versions(self):
        """Iterates through all Monotone interface versions.

        Mocks out bits of setuptools_mtn where appropriate.

        """
        for version in self.versions:
            print "mocking version %r" % (version,)
            factory = MockMonotoneFactory(version, INVENTORIES[version])
            for name in self.mocked:
                mock_name = "mock_" + name
                setattr(setuptools_mtn, name, getattr(factory, mock_name))
            yield factory

    def test_empty_dir_string(self):
        for factory in self.mock_for_versions():
            inventory = factory.find_files_in_mtn("")
            assert set(inventory) == ALL_EXPECTED_FILES

    def test_subdir(self):
        for factory in self.mock_for_versions():
            inventory = factory.find_files_in_mtn("subdir1")
            assert set(inventory) == SUBDIR_EXPECTED_FILES

    def test_common_prefix(self):
        for factory in self.mock_for_versions():
            inventory = factory.find_files_in_mtn("prefix")
            assert set(inventory) == PREFIX_EXPECTED_FILES

def test_no_mtn_root():
    # I hope your / isn't under Monotone control.
    assert not list(setuptools_mtn.find_files_in_mtn("/"))
