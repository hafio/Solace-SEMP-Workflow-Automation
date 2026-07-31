// Package modules implements the idempotent SEMP action modules and their
// registry. Each module file registers its actions via init(), which the
// registry collects at startup.
package modules

import (
	stderrors "errors"

	wferrors "semp-workflow/internal/errors"
	"semp-workflow/internal/models"
	"semp-workflow/internal/semp"
)

// Client is the subset of the SEMP client that action modules depend on. The
// concrete *semp.Client satisfies it structurally in production; tests inject a
// fake that implements the same interface.
type Client interface {
	Exists(path string) (bool, map[string]any, error)
	Create(path string, payload map[string]any) (map[string]any, error)
	Update(path string, payload map[string]any) (map[string]any, error)
	Delete(path string) error
}

// ParamSpec describes a single module parameter. It is stored as an ordered
// slice (Go maps do not preserve insertion order) so generated module
// documentation is stable.
type ParamSpec struct {
	Name        string
	Type        string
	Required    bool
	Default     any
	Description string
	Enum        []string
}

// Module is a single idempotent SEMP action.
type Module interface {
	// Execute runs the action idempotently and returns its result.
	Execute(c Client, args map[string]any, dryRun bool) models.ActionResult
	// Description returns the one-line description used in docs and listings.
	Description() string
	// Params returns the ordered parameter schema used for documentation.
	Params() []ParamSpec
}

// argStr returns args[key] rendered as a string via Stringify, or def when the
// key is absent or nil.
func argStr(args map[string]any, key, def string) string {
	if v, ok := args[key]; ok && v != nil {
		return semp.Stringify(v)
	}
	return def
}

// coerceBoolFields coerces the named fields to bool in place, if present.
func coerceBoolFields(payload map[string]any, fields ...string) {
	for _, f := range fields {
		if v, ok := payload[f]; ok {
			payload[f] = semp.CoerceBool(v)
		}
	}
}

// coerceIntFields coerces the named fields to int in place, if present. The
// first field that fails to parse returns its error, which surfaces as a
// FAILED task.
func coerceIntFields(payload map[string]any, fields ...string) error {
	for _, f := range fields {
		if v, ok := payload[f]; ok {
			n, err := semp.CoerceInt(v)
			if err != nil {
				return err
			}
			payload[f] = n
		}
	}
	return nil
}

// sempCodeOf returns the SEMP error code carried by err, or 0 if err is not a
// *SEMPError.
func sempCodeOf(err error) int {
	var se *wferrors.SEMPError
	if stderrors.As(err, &se) {
		return se.SempCode
	}
	return 0
}

// failed is a small constructor for a FAILED ActionResult.
func failed(msg string) models.ActionResult {
	return models.NewActionResult(models.StatusFailed, msg)
}

// ok is a small constructor for an OK ActionResult.
func ok(msg string) models.ActionResult {
	return models.NewActionResult(models.StatusOK, msg)
}

// skipped is a small constructor for a SKIPPED ActionResult.
func skipped(msg string) models.ActionResult {
	return models.NewActionResult(models.StatusSkipped, msg)
}

// dryrun is a small constructor for a DRYRUN ActionResult.
func dryrun(msg string) models.ActionResult {
	return models.NewActionResult(models.StatusDryRun, msg)
}
