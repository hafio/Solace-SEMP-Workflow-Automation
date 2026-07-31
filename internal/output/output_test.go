package output

import (
	"bytes"
	"strings"
	"testing"

	"github.com/fatih/color"
	"github.com/stretchr/testify/assert"

	"semp-workflow/internal/models"
	"semp-workflow/internal/modules"
)

// capture redirects Out/ErrOut to buffers for the duration of a test and
// disables ANSI color so assertions match plain text.
func capture(t *testing.T) (*bytes.Buffer, *bytes.Buffer) {
	t.Helper()
	origNoColor := color.NoColor
	color.NoColor = true
	origOut, origErr := Out, ErrOut
	var out, errOut bytes.Buffer
	Out, ErrOut = &out, &errOut
	t.Cleanup(func() {
		Out, ErrOut = origOut, origErr
		color.NoColor = origNoColor
	})
	return &out, &errOut
}

func TestPrintTaskResultLabels(t *testing.T) {
	cases := []struct {
		status models.ResultStatus
		label  string
	}{
		{models.StatusOK, "changed"},
		{models.StatusDryRun, "dryrun"},
		{models.StatusSkipped, "skipped"},
		{models.StatusFailed, "FAILED"},
	}
	for _, tc := range cases {
		out, _ := capture(t)
		PrintTaskResult(models.ActionResult{Status: tc.status, TaskName: "Do thing"})
		assert.Contains(t, out.String(), "TASK [Do thing]")
		assert.Contains(t, out.String(), tc.label)
	}
}

func TestPrintTaskResultMessage(t *testing.T) {
	out, _ := capture(t)
	PrintTaskResult(models.ActionResult{Status: models.StatusFailed, TaskName: "T", Message: "boom"})
	s := out.String()
	assert.Contains(t, s, "=> boom")
}

func TestPrintTaskResultFallsBackToModuleName(t *testing.T) {
	out, _ := capture(t)
	PrintTaskResult(models.ActionResult{Status: models.StatusOK, Module: "queue.add"})
	assert.Contains(t, out.String(), "TASK [queue.add]")
}

func TestPrintRecapCountsAndReturn(t *testing.T) {
	out, _ := capture(t)
	results := []models.WorkflowResult{
		{
			WorkflowName: "WF1",
			TaskResults: []models.ActionResult{
				{Status: models.StatusOK},
				{Status: models.StatusSkipped},
				{Status: models.StatusFailed},
			},
		},
	}
	failed := PrintRecap(results)
	assert.True(t, failed)
	s := out.String()
	assert.Contains(t, s, "changed=1")
	assert.Contains(t, s, "skipped=1")
	assert.Contains(t, s, "failed=1")
	assert.Contains(t, s, "Some tasks failed!")
}

func TestPrintRecapAllSuccess(t *testing.T) {
	out, _ := capture(t)
	results := []models.WorkflowResult{
		{WorkflowName: "WF1", TaskResults: []models.ActionResult{{Status: models.StatusOK}}},
	}
	failed := PrintRecap(results)
	assert.False(t, failed)
	assert.Contains(t, out.String(), "All tasks completed successfully.")
}

func TestPrintModuleList(t *testing.T) {
	out, _ := capture(t)
	PrintModuleList([]string{"queue.add", "queue.delete", "rdp.add"})
	s := out.String()
	assert.Contains(t, s, "queue")
	assert.Contains(t, s, "- queue.add")
	assert.Contains(t, s, "- queue.delete")
	assert.Contains(t, s, "- rdp.add")
}

func TestPrintError(t *testing.T) {
	_, errOut := capture(t)
	PrintError("something failed")
	assert.Contains(t, errOut.String(), "ERROR: something failed")
}

func TestRenderModuleDocsMDStructure(t *testing.T) {
	md := RenderModuleDocsMD(modules.Info())

	// Title + legend.
	assert.True(t, strings.HasPrefix(md, "# SEMP Workflow Automation — Module Reference"))
	assert.Contains(t, md, "All actions are **idempotent**")

	// TOC anchor: object prefix underscores become dashes.
	assert.Contains(t, md, "[acl_publish_exception](#acl-publish-exception)")

	// Section headers and per-action headings.
	assert.Contains(t, md, "## queue")
	assert.Contains(t, md, "### `queue.add`")

	// Param table header rendered for a module with params.
	assert.Contains(t, md, "| Parameter | Type | Required | Default | Description |")
}
