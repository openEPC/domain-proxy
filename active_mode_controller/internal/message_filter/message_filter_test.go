package message_filter_test

import (
	"testing"

	"github.com/domain-proxy/active_move_controller/api/active_mode"
	"github.com/domain-proxy/active_move_controller/api/requests"
	"github.com/domain-proxy/active_move_controller/internal/message_filter"
	"github.com/stretchr/testify/assert"
)

func TestFilterMessages(t *testing.T) {
	state := &active_mode.State{
		ActiveModeConfigs: []*active_mode.ActiveModeConfig{{
			Cbsd: &active_mode.Cbsd{
				PendingRequests: []string{"A1", "B1"},
			},
		}, {
			Cbsd: &active_mode.Cbsd{
				PendingRequests: []string{"B2", "C2"},
			},
		}},
	}
	messages := []*requests.RequestPayload{
		{Payload: "A1"},
		{Payload: "B1"},
		{Payload: "C1"},
		{Payload: "A2"},
		{Payload: "B2"},
	}
	expected := []*requests.RequestPayload{
		messages[2], messages[3],
	}
	actual := message_filter.FilterMessages(state, messages)
	assert.Equal(t, expected, actual)
}
