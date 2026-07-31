package modules

import (
	stderrors "errors"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"

	"semp-workflow/internal/models"
)

// --- acl_publish_exception.delete ----------------------------------------

func TestPublishExceptionDelete(t *testing.T) {
	// Missing aclProfileName -> FAILED.
	res := exec(t, "acl_publish_exception.delete", absent(), map[string]any{"publishTopicException": "t"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "aclProfileName")

	// Missing publishTopicException -> FAILED.
	res = exec(t, "acl_publish_exception.delete", absent(), map[string]any{"aclProfileName": "P"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "publishTopicException")

	args := map[string]any{"aclProfileName": "P", "publishTopicException": "SITEA/>"}

	// Absent -> SKIPPED (no Delete issued).
	fc := absent()
	res = exec(t, "acl_publish_exception.delete", fc, args, false)
	assert.Equal(t, models.StatusSkipped, res.Status)
	assert.Equal(t, 0, fc.deletedCount)

	// Present + dryRun -> DRYRUN (no Delete issued).
	fc = existing()
	res = exec(t, "acl_publish_exception.delete", fc, args, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc.deletedCount)

	// Present -> OK; the composite "{syntax},{topic}" segment is deleted.
	fc = existing()
	res = exec(t, "acl_publish_exception.delete", fc, args, false)
	assert.Equal(t, models.StatusOK, res.Status)
	assert.Equal(t, "aclProfiles/P/publishTopicExceptions/smf,SITEA%2F%3E", fc.deletePath)
	assert.Equal(t, 1, fc.deletedCount)

	// Delete returns an error -> FAILED.
	fc = existing()
	fc.onDelete = func(string) error { return stderrors.New("boom") }
	res = exec(t, "acl_publish_exception.delete", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to remove publish topic exception")
}

// --- acl_subscribe_exception.delete --------------------------------------

func TestSubscribeExceptionDelete(t *testing.T) {
	// Missing aclProfileName -> FAILED.
	res := exec(t, "acl_subscribe_exception.delete", absent(), map[string]any{"subscribeTopicException": "t"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "aclProfileName")

	// Missing subscribeTopicException -> FAILED.
	res = exec(t, "acl_subscribe_exception.delete", absent(), map[string]any{"aclProfileName": "P"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "subscribeTopicException")

	args := map[string]any{"aclProfileName": "P", "subscribeTopicException": "SITEA/>"}

	// Absent -> SKIPPED (no Delete issued).
	fc := absent()
	res = exec(t, "acl_subscribe_exception.delete", fc, args, false)
	assert.Equal(t, models.StatusSkipped, res.Status)
	assert.Equal(t, 0, fc.deletedCount)

	// Present + dryRun -> DRYRUN (no Delete issued).
	fc = existing()
	res = exec(t, "acl_subscribe_exception.delete", fc, args, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc.deletedCount)

	// Present -> OK; the composite "{syntax},{topic}" segment is deleted.
	fc = existing()
	res = exec(t, "acl_subscribe_exception.delete", fc, args, false)
	assert.Equal(t, models.StatusOK, res.Status)
	assert.Equal(t, "aclProfiles/P/subscribeTopicExceptions/smf,SITEA%2F%3E", fc.deletePath)
	assert.Equal(t, 1, fc.deletedCount)

	// Delete returns an error -> FAILED.
	fc = existing()
	fc.onDelete = func(string) error { return stderrors.New("boom") }
	res = exec(t, "acl_subscribe_exception.delete", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to remove subscribe topic exception")
}

// --- client_profile.delete -----------------------------------------------

func TestClientProfileDelete(t *testing.T) {
	// Missing name -> FAILED.
	res := exec(t, "client_profile.delete", absent(), map[string]any{}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Missing required arg: clientProfileName")

	// Name too long -> FAILED (broker limit is 32).
	res = exec(t, "client_profile.delete", absent(), map[string]any{"clientProfileName": strings.Repeat("x", 33)}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "32")

	args := map[string]any{"clientProfileName": "CP"}

	// Absent -> SKIPPED.
	res = exec(t, "client_profile.delete", absent(), args, false)
	assert.Equal(t, models.StatusSkipped, res.Status)

	// Present + dryRun -> DRYRUN (no Delete issued).
	fc := existing()
	res = exec(t, "client_profile.delete", fc, args, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc.deletedCount)

	// Present -> OK.
	fc = existing()
	res = exec(t, "client_profile.delete", fc, args, false)
	assert.Equal(t, models.StatusOK, res.Status)
	assert.Equal(t, "clientProfiles/CP", fc.deletePath)

	// Delete returns an error -> FAILED.
	fc = existing()
	fc.onDelete = func(string) error { return stderrors.New("boom") }
	res = exec(t, "client_profile.delete", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to delete client profile")
}

// --- rdp_qb.delete --------------------------------------------------------

func TestQueueBindingDelete(t *testing.T) {
	// Missing args -> FAILED.
	res := exec(t, "rdp_qb.delete", absent(), map[string]any{"restDeliveryPointName": "RDP"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Missing required args")

	args := map[string]any{"restDeliveryPointName": "RDP", "queueBindingName": "Q"}

	// Absent -> SKIPPED.
	res = exec(t, "rdp_qb.delete", absent(), args, false)
	assert.Equal(t, models.StatusSkipped, res.Status)

	// Present + dryRun -> DRYRUN (no Delete issued).
	fc := existing()
	res = exec(t, "rdp_qb.delete", fc, args, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc.deletedCount)

	// Present -> OK.
	fc = existing()
	res = exec(t, "rdp_qb.delete", fc, args, false)
	assert.Equal(t, models.StatusOK, res.Status)
	assert.Equal(t, "restDeliveryPoints/RDP/queueBindings/Q", fc.deletePath)

	// Delete returns an error -> FAILED.
	fc = existing()
	fc.onDelete = func(string) error { return stderrors.New("boom") }
	res = exec(t, "rdp_qb.delete", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to delete queue binding")
}

// --- rdp_rc.delete --------------------------------------------------------

func TestRestConsumerDelete(t *testing.T) {
	// Missing args -> FAILED.
	res := exec(t, "rdp_rc.delete", absent(), map[string]any{"restDeliveryPointName": "RDP"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Missing required args")

	args := map[string]any{"restDeliveryPointName": "RDP", "restConsumerName": "RC"}

	// Absent -> SKIPPED.
	res = exec(t, "rdp_rc.delete", absent(), args, false)
	assert.Equal(t, models.StatusSkipped, res.Status)

	// Present + dryRun -> DRYRUN (no Delete issued).
	fc := existing()
	res = exec(t, "rdp_rc.delete", fc, args, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc.deletedCount)

	// Present -> OK.
	fc = existing()
	res = exec(t, "rdp_rc.delete", fc, args, false)
	assert.Equal(t, models.StatusOK, res.Status)
	assert.Equal(t, "restDeliveryPoints/RDP/restConsumers/RC", fc.deletePath)

	// Delete returns an error -> FAILED.
	fc = existing()
	fc.onDelete = func(string) error { return stderrors.New("boom") }
	res = exec(t, "rdp_rc.delete", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to delete REST consumer")
}

// --- client_username.update (fields-present branch) ----------------------

func TestClientUsernameUpdateAppliesFields(t *testing.T) {
	// Exists with updatable fields -> Update issued, name key dropped, OK.
	fc := existing()
	res := exec(t, "client_username.update", fc, map[string]any{
		"clientUsername":    "svc",
		"clientProfileName": "cp",
		"aclProfileName":    "acl-x",
		"enabled":           "false",
	}, false)
	assert.Equal(t, models.StatusOK, res.Status)
	assert.Equal(t, "clientUsernames/svc", fc.updatePath)
	assert.NotContains(t, fc.updateBody, "clientUsername")
	assert.Equal(t, false, fc.updateBody["enabled"])
	assert.Equal(t, "cp", fc.updateBody["clientProfileName"])
	assert.Equal(t, "acl-x", fc.updateBody["aclProfileName"]) // both profile associations applied
	assert.Equal(t, 1, fc.updatedCount)

	// Exists but only the name -> nothing to update.
	res = exec(t, "client_username.update", existing(), map[string]any{"clientUsername": "svc"}, false)
	assert.Equal(t, models.StatusSkipped, res.Status)
	assert.Contains(t, res.Message, "No fields to update")

	// Exists with fields + dryRun -> DRYRUN (no Update issued).
	fc = existing()
	res = exec(t, "client_username.update", fc, map[string]any{"clientUsername": "svc", "enabled": "true"}, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc.updatedCount)

	// Update returns an error -> FAILED.
	fc = existing()
	fc.onUpdate = func(string, map[string]any) (map[string]any, error) { return nil, stderrors.New("boom") }
	res = exec(t, "client_username.update", fc, map[string]any{"clientUsername": "svc", "enabled": "true"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to update client username")
}

// --- q_sub.delete (remaining branches) -----------------------------------

func TestSubscriptionDeleteBranches(t *testing.T) {
	// Missing args -> FAILED.
	res := exec(t, "q_sub.delete", absent(), map[string]any{"queueName": "Q"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Missing required args")

	args := map[string]any{"queueName": "Q", "subscriptionTopic": "SITEA/>"}

	// Exists check errors -> FAILED.
	fc := &fakeClient{onExists: func(string) (bool, map[string]any, error) {
		return false, nil, stderrors.New("boom")
	}}
	res = exec(t, "q_sub.delete", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Error checking subscription")

	// Present + dryRun -> DRYRUN (no Delete issued).
	fc2 := existing()
	res = exec(t, "q_sub.delete", fc2, args, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc2.deletedCount)

	// Present -> OK; topic is encoded in the path segment.
	fc2 = existing()
	res = exec(t, "q_sub.delete", fc2, args, false)
	assert.Equal(t, models.StatusOK, res.Status)
	assert.Equal(t, "queues/Q/subscriptions/SITEA%2F%3E", fc2.deletePath)

	// Delete returns an error -> FAILED.
	fc2 = existing()
	fc2.onDelete = func(string) error { return stderrors.New("boom") }
	res = exec(t, "q_sub.delete", fc2, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to remove subscription")
}

// --- acl_profile.delete (remaining branches) -----------------------------

func TestAclProfileDeleteBranches(t *testing.T) {
	// Missing name -> FAILED.
	res := exec(t, "acl_profile.delete", absent(), map[string]any{}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Missing required arg: aclProfileName")

	// Exists check errors -> FAILED.
	fc := &fakeClient{onExists: func(string) (bool, map[string]any, error) {
		return false, nil, stderrors.New("boom")
	}}
	res = exec(t, "acl_profile.delete", fc, map[string]any{"aclProfileName": "P"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Error checking ACL profile")

	// Present + dryRun -> DRYRUN (no Delete issued).
	fc2 := existing()
	res = exec(t, "acl_profile.delete", fc2, map[string]any{"aclProfileName": "P"}, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc2.deletedCount)

	// Present -> OK.
	fc2 = existing()
	res = exec(t, "acl_profile.delete", fc2, map[string]any{"aclProfileName": "P"}, false)
	assert.Equal(t, models.StatusOK, res.Status)
	assert.Equal(t, "aclProfiles/P", fc2.deletePath)

	// Delete returns an error -> FAILED.
	fc2 = existing()
	fc2.onDelete = func(string) error { return stderrors.New("boom") }
	res = exec(t, "acl_profile.delete", fc2, map[string]any{"aclProfileName": "P"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to delete ACL profile")
}

// --- queue.delete / queue.update (remaining branches) --------------------

func TestQueueDeleteAndUpdateErrorBranches(t *testing.T) {
	// delete: missing name -> FAILED.
	res := exec(t, "queue.delete", absent(), map[string]any{}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Missing required arg: queueName")

	// delete: Exists check errors -> FAILED.
	fc := &fakeClient{onExists: func(string) (bool, map[string]any, error) {
		return false, nil, stderrors.New("boom")
	}}
	res = exec(t, "queue.delete", fc, map[string]any{"queueName": "Q"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Error checking queue")

	// delete: Delete error -> FAILED.
	fcd := existing()
	fcd.onDelete = func(string) error { return stderrors.New("boom") }
	res = exec(t, "queue.delete", fcd, map[string]any{"queueName": "Q"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to delete queue")

	// update: missing name -> FAILED.
	res = exec(t, "queue.update", absent(), map[string]any{}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Missing required arg: queueName")

	// update: bad int coercion -> FAILED (payload build error).
	res = exec(t, "queue.update", existing(), map[string]any{"queueName": "Q", "maxTtl": "abc"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "invalid literal for int()")

	// update: present with fields + dryRun -> DRYRUN (no Update issued).
	fcu := existing()
	res = exec(t, "queue.update", fcu, map[string]any{"queueName": "Q", "egressEnabled": "false"}, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fcu.updatedCount)

	// update: Update error -> FAILED.
	fcu = existing()
	fcu.onUpdate = func(string, map[string]any) (map[string]any, error) { return nil, stderrors.New("boom") }
	res = exec(t, "queue.update", fcu, map[string]any{"queueName": "Q", "egressEnabled": "false"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to update queue")
}

// --- rdp.delete / rdp.update (remaining branches) ------------------------

func TestRdpDeleteAndUpdateErrorBranches(t *testing.T) {
	// delete: missing name -> FAILED.
	res := exec(t, "rdp.delete", absent(), map[string]any{}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Missing required arg: restDeliveryPointName")

	// delete: absent -> SKIPPED.
	res = exec(t, "rdp.delete", absent(), map[string]any{"restDeliveryPointName": "RDP"}, false)
	assert.Equal(t, models.StatusSkipped, res.Status)

	// delete: present + dryRun -> DRYRUN (no Delete issued).
	fc := existing()
	res = exec(t, "rdp.delete", fc, map[string]any{"restDeliveryPointName": "RDP"}, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc.deletedCount)

	// delete: Delete error -> FAILED.
	fc = existing()
	fc.onDelete = func(string) error { return stderrors.New("boom") }
	res = exec(t, "rdp.delete", fc, map[string]any{"restDeliveryPointName": "RDP"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to delete RDP")

	// update: exists but only the name -> nothing to update.
	res = exec(t, "rdp.update", existing(), map[string]any{"restDeliveryPointName": "RDP"}, false)
	assert.Equal(t, models.StatusSkipped, res.Status)
	assert.Contains(t, res.Message, "No fields to update")

	// update: present with fields + dryRun -> DRYRUN (no Update issued).
	fcu := existing()
	res = exec(t, "rdp.update", fcu, map[string]any{"restDeliveryPointName": "RDP", "enabled": "false"}, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fcu.updatedCount)

	// update: Update error -> FAILED.
	fcu = existing()
	fcu.onUpdate = func(string, map[string]any) (map[string]any, error) { return nil, stderrors.New("boom") }
	res = exec(t, "rdp.update", fcu, map[string]any{"restDeliveryPointName": "RDP", "enabled": "false"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to update RDP")
}

// --- rdp_rc.add (remaining branches) -------------------------------------

func TestRestConsumerAddBranches(t *testing.T) {
	// Missing restDeliveryPointName -> FAILED.
	res := exec(t, "rdp_rc.add", absent(), map[string]any{"restConsumerName": "RC"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Missing required args")

	// Missing restConsumerName -> FAILED.
	res = exec(t, "rdp_rc.add", absent(), map[string]any{"restDeliveryPointName": "RDP"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Missing required args")

	args := map[string]any{"restDeliveryPointName": "RDP", "restConsumerName": "RC"}

	// Exists -> SKIPPED (no Create issued).
	fc := existing()
	res = exec(t, "rdp_rc.add", fc, args, false)
	assert.Equal(t, models.StatusSkipped, res.Status)
	assert.Equal(t, 0, fc.createdCount)

	// Absent + dryRun -> DRYRUN (no Create issued).
	fc = absent()
	res = exec(t, "rdp_rc.add", fc, args, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc.createdCount)

	// Exists check errors -> FAILED.
	fc = &fakeClient{onExists: func(string) (bool, map[string]any, error) {
		return false, nil, stderrors.New("boom")
	}}
	res = exec(t, "rdp_rc.add", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Error checking REST consumer")

	// Create errors -> FAILED.
	fc = absent()
	fc.onCreate = func(string, map[string]any) (map[string]any, error) { return nil, stderrors.New("boom") }
	res = exec(t, "rdp_rc.add", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to create REST consumer")

	// outgoingConnectionCount is coerced to int on the create path.
	fc = absent()
	res = exec(t, "rdp_rc.add", fc, map[string]any{
		"restDeliveryPointName":   "RDP",
		"restConsumerName":        "RC",
		"outgoingConnectionCount": "5",
	}, false)
	assert.Equal(t, models.StatusOK, res.Status)
	assert.Equal(t, 5, fc.createBody["outgoingConnectionCount"])
}

// --- rdp_qb.add (remaining branches) -------------------------------------

func TestQueueBindingAddBranches(t *testing.T) {
	// Missing args -> FAILED.
	res := exec(t, "rdp_qb.add", absent(), map[string]any{"restDeliveryPointName": "RDP"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Missing required args")

	// queueBindingName too long -> FAILED (broker limit is 200).
	res = exec(t, "rdp_qb.add", absent(), map[string]any{
		"restDeliveryPointName": "RDP",
		"queueBindingName":      strings.Repeat("x", 201),
	}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "200")

	args := map[string]any{"restDeliveryPointName": "RDP", "queueBindingName": "Q"}

	// Absent + dryRun -> DRYRUN (no Create issued).
	fc := absent()
	res = exec(t, "rdp_qb.add", fc, args, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc.createdCount)

	// Exists check errors -> FAILED.
	fc = &fakeClient{onExists: func(string) (bool, map[string]any, error) {
		return false, nil, stderrors.New("boom")
	}}
	res = exec(t, "rdp_qb.add", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Error checking queue binding")

	// Create errors (a non-AlreadyExists SEMP error) -> FAILED.
	fc = absent()
	fc.onCreate = func(string, map[string]any) (map[string]any, error) { return nil, stderrors.New("boom") }
	res = exec(t, "rdp_qb.add", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to create queue binding")
}

// --- acl_publish_exception.add (remaining branches) ----------------------

func TestPublishExceptionAddBranches(t *testing.T) {
	args := map[string]any{"aclProfileName": "P", "publishTopicException": "SITEA/>"}

	// Exists -> SKIPPED (no Create issued).
	fc := existing()
	res := exec(t, "acl_publish_exception.add", fc, args, false)
	assert.Equal(t, models.StatusSkipped, res.Status)
	assert.Equal(t, 0, fc.createdCount)

	// Absent + dryRun -> DRYRUN (no Create issued).
	fc = absent()
	res = exec(t, "acl_publish_exception.add", fc, args, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc.createdCount)

	// Exists check errors -> FAILED.
	fc = &fakeClient{onExists: func(string) (bool, map[string]any, error) {
		return false, nil, stderrors.New("boom")
	}}
	res = exec(t, "acl_publish_exception.add", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Error checking publish topic exception")

	// Create errors -> FAILED.
	fc = absent()
	fc.onCreate = func(string, map[string]any) (map[string]any, error) { return nil, stderrors.New("boom") }
	res = exec(t, "acl_publish_exception.add", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to add publish topic exception")
}

// --- acl_subscribe_exception.add (remaining branches) --------------------

func TestSubscribeExceptionAddBranches(t *testing.T) {
	// Missing aclProfileName -> FAILED.
	res := exec(t, "acl_subscribe_exception.add", absent(), map[string]any{"subscribeTopicException": "t"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "aclProfileName")

	// Missing subscribeTopicException -> FAILED.
	res = exec(t, "acl_subscribe_exception.add", absent(), map[string]any{"aclProfileName": "P"}, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "subscribeTopicException")

	args := map[string]any{"aclProfileName": "P", "subscribeTopicException": "SITEA/>"}

	// Exists -> SKIPPED (no Create issued).
	fc := existing()
	res = exec(t, "acl_subscribe_exception.add", fc, args, false)
	assert.Equal(t, models.StatusSkipped, res.Status)
	assert.Equal(t, 0, fc.createdCount)

	// Absent + dryRun -> DRYRUN (no Create issued).
	fc = absent()
	res = exec(t, "acl_subscribe_exception.add", fc, args, true)
	assert.Equal(t, models.StatusDryRun, res.Status)
	assert.Equal(t, 0, fc.createdCount)

	// Exists check errors -> FAILED.
	fc = &fakeClient{onExists: func(string) (bool, map[string]any, error) {
		return false, nil, stderrors.New("boom")
	}}
	res = exec(t, "acl_subscribe_exception.add", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Error checking subscribe topic exception")

	// Create errors -> FAILED.
	fc = absent()
	fc.onCreate = func(string, map[string]any) (map[string]any, error) { return nil, stderrors.New("boom") }
	res = exec(t, "acl_subscribe_exception.add", fc, args, false)
	assert.Equal(t, models.StatusFailed, res.Status)
	assert.Contains(t, res.Message, "Failed to add subscribe topic exception")

	// OK path defaults the syntax to smf and posts to the collection path.
	fc = absent()
	res = exec(t, "acl_subscribe_exception.add", fc, args, false)
	assert.Equal(t, models.StatusOK, res.Status)
	assert.Equal(t, "aclProfiles/P/subscribeTopicExceptions", fc.createPath)
	assert.Equal(t, "smf", fc.createBody["subscribeTopicExceptionSyntax"])
}
