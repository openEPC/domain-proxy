package message_filter

import (
	"github.com/domain-proxy/active_move_controller/api/active_mode"
	"github.com/domain-proxy/active_move_controller/api/requests"
)

func FilterMessages(state *active_mode.State, messages []*requests.RequestPayload) []*requests.RequestPayload {
	set := map[string]bool{}
	for _, config := range state.ActiveModeConfigs {
		for _, m := range config.GetCbsd().GetPendingRequests() {
			set[m] = true
		}
	}
	filtered := make([]*requests.RequestPayload, 0, len(messages))
	for _, m := range messages {
		if !set[m.Payload] {
			filtered = append(filtered, m)
		}
	}
	return filtered
}
