"""
Unit Tests for Unified Approval Service

Tests all approval workflow functionality:
- Creating approval requests
- Multi-level approvals
- Rejection workflows
- History tracking
- Configuration management
"""

import pytest
from datetime import datetime
from extensions import db
from approval_management.models.approval import (
    ApprovalRequest,
    ApprovalHistory,
    ApprovalConfiguration
)
from approval_management.services.approval_service import ApprovalService
from constants import ApprovalStatus


class TestApprovalRequestCreation:
    """Test creating approval requests"""

    def test_create_single_level_approval(self):
        """Create approval with one level"""
        result = ApprovalService.create_approval_request(
            entity_type='invoice',
            entity_id=123,
            company_id=1,
            created_by_id=10,
            total_levels=1
        )

        assert result[1] in (200, 201)
        data = result[0].json['data']
        assert data['entity_type'] == 'invoice'
        assert data['entity_id'] == 123
        assert data['status'] == ApprovalStatus.PENDING.value
        assert data['total_levels'] == 1

    def test_create_multi_level_approval(self):
        """Create approval with multiple levels"""
        result = ApprovalService.create_approval_request(
            entity_type='purchase',
            entity_id=456,
            company_id=1,
            created_by_id=10,
            total_levels=3,
            approval_type='sequential'
        )

        assert result[1] in (200, 201)
        data = result[0].json['data']
        assert data['total_levels'] == 3
        assert data['approval_type'] == 'sequential'

    def test_create_with_required_approvers(self):
        """Create approval with specific required approvers"""
        result = ApprovalService.create_approval_request(
            entity_type='budget',
            entity_id=789,
            company_id=1,
            created_by_id=10,
            total_levels=2,
            required_approver_ids=[20, 21]
        )

        assert result[1] in (200, 201)
        data = result[0].json['data']
        assert data['required_approver_ids'] == [20, 21]


class TestApprovalWorkflow:
    """Test approval workflow operations"""

    def test_single_level_approval_completes(self):
        """Single level approval marks request as fully approved"""
        # Create approval
        create_result = ApprovalService.create_approval_request(
            entity_type='invoice',
            entity_id=123,
            company_id=1,
            created_by_id=10,
            total_levels=1
        )

        approval_id = create_result[0].json['data']['id']

        # Approve
        approve_result = ApprovalService.approve(
            approval_id=approval_id,
            approver_id=20,
            notes="Looks good"
        )

        assert approve_result[1] == 200
        data = approve_result[0].json['data']
        assert data['status'] == ApprovalStatus.APPROVED.value
        assert data['approved_by_id'] == 20

    def test_multi_level_approval_advances_levels(self):
        """Multi-level approval advances through levels"""
        # Create 2-level approval
        create_result = ApprovalService.create_approval_request(
            entity_type='purchase',
            entity_id=456,
            company_id=1,
            created_by_id=10,
            total_levels=2
        )

        approval_id = create_result[0].json['data']['id']

        # Approve level 1
        result1 = ApprovalService.approve(
            approval_id=approval_id,
            approver_id=20,
            notes="Level 1 approved"
        )

        data1 = result1[0].json['data']
        assert data1['status'] == ApprovalStatus.PENDING.value  # Still pending level 2
        assert data1['approval_level'] == 2  # Advanced to level 2

        # Approve level 2
        result2 = ApprovalService.approve(
            approval_id=approval_id,
            approver_id=21,
            notes="Level 2 approved"
        )

        data2 = result2[0].json['data']
        assert data2['status'] == ApprovalStatus.APPROVED.value  # Fully approved

    def test_rejection_blocks_further_approval(self):
        """Rejecting prevents further approval"""
        # Create approval
        create_result = ApprovalService.create_approval_request(
            entity_type='invoice',
            entity_id=123,
            company_id=1,
            created_by_id=10,
            total_levels=2
        )

        approval_id = create_result[0].json['data']['id']

        # Reject
        reject_result = ApprovalService.reject(
            approval_id=approval_id,
            rejector_id=20,
            reason="Amount too high"
        )

        assert reject_result[1] == 200
        data = reject_result[0].json['data']
        assert data['status'] == ApprovalStatus.REJECTED.value
        assert data['rejection_reason'] == "Amount too high"

        # Try to approve rejected request - should fail
        approve_result = ApprovalService.approve(
            approval_id=approval_id,
            approver_id=21,
            notes="Trying to approve rejected request"
        )

        assert approve_result[1] == 400  # Should fail


class TestApprovalHistory:
    """Test approval history tracking"""

    def test_history_created_on_approval(self):
        """History entry created when approval happens"""
        # Create approval
        create_result = ApprovalService.create_approval_request(
            entity_type='invoice',
            entity_id=123,
            company_id=1,
            created_by_id=10,
            total_levels=1
        )

        approval_id = create_result[0].json['data']['id']

        # Approve
        ApprovalService.approve(
            approval_id=approval_id,
            approver_id=20,
            notes="Approved"
        )

        # Get history
        history_result = ApprovalService.get_approval_history(approval_id)

        assert history_result[1] == 200
        history = history_result[0].json['data']

        # Should have 'created' and 'approved' entries
        actions = [h['action'] for h in history]
        assert 'created' in actions
        assert 'approved' in actions

    def test_history_tracks_approver(self):
        """History correctly records who approved"""
        # Create and approve
        create_result = ApprovalService.create_approval_request(
            entity_type='invoice',
            entity_id=123,
            company_id=1,
            created_by_id=10,
            total_levels=1
        )

        approval_id = create_result[0].json['data']['id']

        ApprovalService.approve(
            approval_id=approval_id,
            approver_id=20,
            notes="Approved"
        )

        # Get history
        history_result = ApprovalService.get_approval_history(approval_id)
        history = history_result[0].json['data']

        # Find approved entry
        approved_entry = next(h for h in history if h['action'] == 'approved')
        assert approved_entry['performed_by_id'] == 20


class TestApprovalConfiguration:
    """Test approval configuration management"""

    def test_set_configuration(self):
        """Set approval configuration for entity type"""
        result = ApprovalService.set_approval_config(
            company_id=1,
            entity_type='invoice',
            total_levels=2,
            approval_type='sequential',
            amount_threshold=50000,
            auto_approve_below=5000
        )

        assert result[1] == 200
        config = result[0].json['data']
        assert config['entity_type'] == 'invoice'
        assert config['total_levels'] == 2
        assert config['amount_threshold'] == 50000

    def test_configuration_applied_to_new_requests(self):
        """New approval requests use stored configuration"""
        # Set configuration
        ApprovalService.set_approval_config(
            company_id=1,
            entity_type='budget',
            total_levels=3,
            approval_type='sequential'
        )

        # Create approval without specifying levels
        result = ApprovalService.create_approval_request(
            entity_type='budget',
            entity_id=789,
            company_id=1,
            created_by_id=10
        )

        # Should use configuration levels
        data = result[0].json['data']
        assert data['total_levels'] == 3


class TestPendingApprovalsQuery:
    """Test retrieving pending approvals"""

    def test_get_pending_for_approver(self):
        """Get pending approvals for specific approver"""
        # Create multiple approvals
        for i in range(3):
            ApprovalService.create_approval_request(
                entity_type='invoice',
                entity_id=100 + i,
                company_id=1,
                created_by_id=10,
                total_levels=1
            )

        # Get pending for approver
        result = ApprovalService.get_pending_approvals(
            company_id=1,
            approver_id=20,
            page=1,
            per_page=10
        )

        assert result[1] == 200
        data = result[0].json['data']
        assert len(data) >= 3

    def test_filter_by_entity_type(self):
        """Filter pending approvals by entity type"""
        # Create invoice approval
        ApprovalService.create_approval_request(
            entity_type='invoice',
            entity_id=123,
            company_id=1,
            created_by_id=10,
            total_levels=1
        )

        # Create purchase approval
        ApprovalService.create_approval_request(
            entity_type='purchase',
            entity_id=456,
            company_id=1,
            created_by_id=10,
            total_levels=1
        )

        # Get pending invoices only
        result = ApprovalService.get_pending_approvals(
            company_id=1,
            entity_type='invoice',
            page=1,
            per_page=10
        )

        data = result[0].json['data']
        for approval in data:
            assert approval['entity_type'] == 'invoice'


class TestApprovalPermissions:
    """Test approval permissions and authorization"""

    def test_can_be_approved_by_assigned_approver(self):
        """Assigned approver can approve"""
        # Create approval with assigned approver
        create_result = ApprovalService.create_approval_request(
            entity_type='invoice',
            entity_id=123,
            company_id=1,
            created_by_id=10,
            total_levels=1,
            required_approver_ids=[20]
        )

        approval = ApprovalRequest.query.get(
            create_result[0].json['data']['id']
        )

        assert approval.can_be_approved_by(20)
        assert not approval.can_be_approved_by(21)

    def test_cannot_approve_if_not_assigned(self):
        """Non-assigned approver cannot approve"""
        # Create approval
        create_result = ApprovalService.create_approval_request(
            entity_type='invoice',
            entity_id=123,
            company_id=1,
            created_by_id=10,
            total_levels=1,
            required_approver_ids=[20]
        )

        approval_id = create_result[0].json['data']['id']

        # Try to approve as different user
        result = ApprovalService.approve(
            approval_id=approval_id,
            approver_id=99,  # Not assigned
            notes="Trying to approve"
        )

        # Should fail with 403 Forbidden
        assert result[1] == 403


# ==================== Integration Test Scenarios ====================

class TestEndToEndScenarios:
    """End-to-end workflow scenarios"""

    def test_complete_invoice_approval_workflow(self):
        """Complete workflow: create invoice, approve, finalize"""
        # 1. Create approval for invoice
        create_result = ApprovalService.create_approval_request(
            entity_type='invoice',
            entity_id=12345,
            company_id=1,
            created_by_id=10,  # Accountant creates
            total_levels=2
        )

        approval_id = create_result[0].json['data']['id']
        assert create_result[1] in (200, 201)

        # 2. Manager approves
        approve1_result = ApprovalService.approve(
            approval_id=approval_id,
            approver_id=20,
            notes="Verified amounts"
        )

        assert approve1_result[1] == 200
        assert approve1_result[0].json['data']['approval_level'] == 2

        # 3. Director approves (final)
        approve2_result = ApprovalService.approve(
            approval_id=approval_id,
            approver_id=30,
            notes="Approved"
        )

        assert approve2_result[1] == 200
        assert approve2_result[0].json['data']['status'] == ApprovalStatus.APPROVED.value

        # 4. Verify complete history
        history_result = ApprovalService.get_approval_history(approval_id)
        history = history_result[0].json['data']

        assert len(history) >= 4  # created, approved×2
        assert history[0]['performed_by_id'] in [10, 20, 30]

    def test_rejection_workflow(self):
        """Workflow: create, partial approval, reject"""
        # 1. Create approval
        create_result = ApprovalService.create_approval_request(
            entity_type='budget',
            entity_id=99999,
            company_id=1,
            created_by_id=10,
            total_levels=2
        )

        approval_id = create_result[0].json['data']['id']

        # 2. Manager rejects
        reject_result = ApprovalService.reject(
            approval_id=approval_id,
            rejector_id=20,
            reason="Budget exceeds project scope"
        )

        assert reject_result[1] == 200
        assert reject_result[0].json['data']['status'] == ApprovalStatus.REJECTED.value

        # 3. Further approval should fail
        approve_result = ApprovalService.approve(
            approval_id=approval_id,
            approver_id=30,
            notes="Trying after rejection"
        )

        assert approve_result[1] == 400
