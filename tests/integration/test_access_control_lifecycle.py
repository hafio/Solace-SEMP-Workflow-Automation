"""Integration: ACL profile, client profile, and client username lifecycle."""

import pytest

from semp_workflow.models import ResultStatus
from semp_workflow.modules.acl_profile import AclProfileAdd, AclProfileDelete
from semp_workflow.modules.client_profile import ClientProfileAdd, ClientProfileDelete
from semp_workflow.modules.client_username import ClientUsernameAdd, ClientUsernameDelete

from .conftest import PREFIX

pytestmark = pytest.mark.integration

ACL_NAME = f"{PREFIX}ACL"
CP_NAME = f"{PREFIX}CLIENT-PROFILE"
CU_NAME = f"{PREFIX}CLIENT-USER"


@pytest.fixture(autouse=True)
def cleanup(semp_client):
    yield
    for path in [
        f"clientUsernames/{semp_client._enc(CU_NAME)}",
        f"clientProfiles/{semp_client._enc(CP_NAME)}",
        f"aclProfiles/{semp_client._enc(ACL_NAME)}",
    ]:
        try:
            semp_client.delete(path)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# ACL Profile
# ---------------------------------------------------------------------------

class TestAclProfileLifecycle:
    def test_add_creates_profile(self, semp_client):
        result = AclProfileAdd().execute(semp_client, {"aclProfileName": ACL_NAME})
        assert result.status == ResultStatus.OK

    def test_add_again_skipped(self, semp_client):
        AclProfileAdd().execute(semp_client, {"aclProfileName": ACL_NAME})
        result = AclProfileAdd().execute(semp_client, {"aclProfileName": ACL_NAME})
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun_not_exists(self, semp_client):
        result = AclProfileAdd().execute(
            semp_client, {"aclProfileName": ACL_NAME}, dry_run=True
        )
        assert result.status == ResultStatus.DRYRUN
        # Confirm nothing was created
        found, _ = semp_client.exists(f"aclProfiles/{semp_client._enc(ACL_NAME)}")
        assert found is False

    def test_delete_removes_profile(self, semp_client):
        AclProfileAdd().execute(semp_client, {"aclProfileName": ACL_NAME})
        result = AclProfileDelete().execute(semp_client, {"aclProfileName": ACL_NAME})
        assert result.status == ResultStatus.OK

    def test_delete_again_skipped(self, semp_client):
        AclProfileAdd().execute(semp_client, {"aclProfileName": ACL_NAME})
        AclProfileDelete().execute(semp_client, {"aclProfileName": ACL_NAME})
        result = AclProfileDelete().execute(semp_client, {"aclProfileName": ACL_NAME})
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun_delete_exists(self, semp_client):
        AclProfileAdd().execute(semp_client, {"aclProfileName": ACL_NAME})
        result = AclProfileDelete().execute(
            semp_client, {"aclProfileName": ACL_NAME}, dry_run=True
        )
        assert result.status == ResultStatus.DRYRUN
        # Confirm it was NOT actually deleted
        found, _ = semp_client.exists(f"aclProfiles/{semp_client._enc(ACL_NAME)}")
        assert found is True


# ---------------------------------------------------------------------------
# Client Profile
# ---------------------------------------------------------------------------

class TestClientProfileLifecycle:
    def test_add_creates_profile(self, semp_client):
        result = ClientProfileAdd().execute(
            semp_client, {"clientProfileName": CP_NAME}
        )
        assert result.status == ResultStatus.OK

    def test_add_again_skipped(self, semp_client):
        ClientProfileAdd().execute(semp_client, {"clientProfileName": CP_NAME})
        result = ClientProfileAdd().execute(semp_client, {"clientProfileName": CP_NAME})
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun_not_exists(self, semp_client):
        result = ClientProfileAdd().execute(
            semp_client, {"clientProfileName": CP_NAME}, dry_run=True
        )
        assert result.status == ResultStatus.DRYRUN
        found, _ = semp_client.exists(f"clientProfiles/{semp_client._enc(CP_NAME)}")
        assert found is False

    def test_add_with_options(self, semp_client):
        result = ClientProfileAdd().execute(
            semp_client,
            {
                "clientProfileName": CP_NAME,
                "allowGuaranteedMsgSendEnabled": True,
                "allowGuaranteedMsgReceiveEnabled": True,
                "maxSubscriptionCount": 100,
            },
        )
        assert result.status == ResultStatus.OK

    def test_delete_removes_profile(self, semp_client):
        ClientProfileAdd().execute(semp_client, {"clientProfileName": CP_NAME})
        result = ClientProfileDelete().execute(
            semp_client, {"clientProfileName": CP_NAME}
        )
        assert result.status == ResultStatus.OK

    def test_delete_again_skipped(self, semp_client):
        ClientProfileAdd().execute(semp_client, {"clientProfileName": CP_NAME})
        ClientProfileDelete().execute(semp_client, {"clientProfileName": CP_NAME})
        result = ClientProfileDelete().execute(
            semp_client, {"clientProfileName": CP_NAME}
        )
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun_delete_exists(self, semp_client):
        ClientProfileAdd().execute(semp_client, {"clientProfileName": CP_NAME})
        result = ClientProfileDelete().execute(
            semp_client, {"clientProfileName": CP_NAME}, dry_run=True
        )
        assert result.status == ResultStatus.DRYRUN
        found, _ = semp_client.exists(f"clientProfiles/{semp_client._enc(CP_NAME)}")
        assert found is True


# ---------------------------------------------------------------------------
# Client Username
# ---------------------------------------------------------------------------

class TestClientUsernameLifecycle:
    def test_add_creates_username(self, semp_client):
        result = ClientUsernameAdd().execute(
            semp_client, {"clientUsername": CU_NAME}
        )
        assert result.status == ResultStatus.OK

    def test_add_again_skipped(self, semp_client):
        ClientUsernameAdd().execute(semp_client, {"clientUsername": CU_NAME})
        result = ClientUsernameAdd().execute(semp_client, {"clientUsername": CU_NAME})
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun_not_exists(self, semp_client):
        result = ClientUsernameAdd().execute(
            semp_client, {"clientUsername": CU_NAME}, dry_run=True
        )
        assert result.status == ResultStatus.DRYRUN
        found, _ = semp_client.exists(f"clientUsernames/{semp_client._enc(CU_NAME)}")
        assert found is False

    def test_delete_removes_username(self, semp_client):
        ClientUsernameAdd().execute(semp_client, {"clientUsername": CU_NAME})
        result = ClientUsernameDelete().execute(
            semp_client, {"clientUsername": CU_NAME}
        )
        assert result.status == ResultStatus.OK

    def test_delete_again_skipped(self, semp_client):
        ClientUsernameAdd().execute(semp_client, {"clientUsername": CU_NAME})
        ClientUsernameDelete().execute(semp_client, {"clientUsername": CU_NAME})
        result = ClientUsernameDelete().execute(
            semp_client, {"clientUsername": CU_NAME}
        )
        assert result.status == ResultStatus.SKIPPED

    def test_dryrun_delete_exists(self, semp_client):
        ClientUsernameAdd().execute(semp_client, {"clientUsername": CU_NAME})
        result = ClientUsernameDelete().execute(
            semp_client, {"clientUsername": CU_NAME}, dry_run=True
        )
        assert result.status == ResultStatus.DRYRUN
        found, _ = semp_client.exists(
            f"clientUsernames/{semp_client._enc(CU_NAME)}"
        )
        assert found is True
