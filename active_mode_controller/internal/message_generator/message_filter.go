package message_generator

import (
	"encoding/json"
)

func filterMessages(pending []string, messages []message) []message {
	set := map[string]bool{}
	for _, m := range pending {
		set[m] = true
	}
	filtered := make([]message, 0, len(messages))
	for _, m := range messages {
		b, _ := json.Marshal(m)
		if !set[string(b)] {
			filtered = append(filtered, m)
		}
	}
	return filtered
}
