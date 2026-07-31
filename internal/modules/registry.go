package modules

import (
	"fmt"
	"sort"
	"strings"
)

// registry maps "object.verb" action names to their Module implementation.
var registry = map[string]Module{}

// register adds a module action to the registry. Called from each module's
// init() at startup.
func register(name string, m Module) {
	registry[name] = m
}

// Get looks up a registered module by "object.verb" name. The error message
// lists the available modules.
func Get(name string) (Module, error) {
	m, ok := registry[name]
	if !ok {
		return nil, fmt.Errorf("Unknown module '%s'. Available: %s", name, strings.Join(List(), ", ")) //nolint:staticcheck // message text is an intentional exact wording
	}
	return m, nil
}

// List returns the sorted names of all registered modules.
func List() []string {
	names := make([]string, 0, len(registry))
	for k := range registry {
		names = append(names, k)
	}
	sort.Strings(names)
	return names
}

// ModuleInfo is the description + parameter schema for a single module.
type ModuleInfo struct {
	Description string
	Params      []ParamSpec
}

// Info returns the description and parameter schema for every registered
// module. Callers that need deterministic ordering should iterate List().
func Info() map[string]ModuleInfo {
	out := make(map[string]ModuleInfo, len(registry))
	for name, m := range registry {
		out[name] = ModuleInfo{Description: m.Description(), Params: m.Params()}
	}
	return out
}
