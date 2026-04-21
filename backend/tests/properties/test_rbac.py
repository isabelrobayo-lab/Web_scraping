"""Property-based tests for RBAC Permission Enforcement (Property 21).

**Validates: Requirements 12.4**

Property 21: For any user with a given role and any API endpoint, access SHALL
be granted if and only if the role's permissions include the required permission
for that endpoint.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.auth.dependencies import RBACMiddleware

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# All defined roles
roles_strategy = st.sampled_from(["administrador", "operador"])

# All defined permissions across all roles
all_permissions = list(
    set(
        perm
        for perms in RBACMiddleware.ROLE_PERMISSIONS.values()
        for perm in perms
    )
)
permissions_strategy = st.sampled_from(all_permissions)

# Unknown roles that should have no permissions
unknown_roles_strategy = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz",
    min_size=3,
    max_size=15,
).filter(lambda r: r not in RBACMiddleware.ROLE_PERMISSIONS)


# ---------------------------------------------------------------------------
# Property tests
# ---------------------------------------------------------------------------


class TestRBACEnforcement:
    """Property 21: RBAC Permission Enforcement."""

    @pytest.mark.property
    @given(role=roles_strategy, permission=permissions_strategy)
    @settings(max_examples=50)
    def test_access_granted_iff_role_has_permission(
        self, role: str, permission: str
    ):
        """For any role and permission, has_permission returns True if and only
        if the permission is in the role's permission list.

        **Validates: Requirements 12.4**
        """
        expected = permission in RBACMiddleware.ROLE_PERMISSIONS[role]
        actual = RBACMiddleware.has_permission(role, permission)
        assert actual == expected, (
            f"Role '{role}' with permission '{permission}': "
            f"expected {expected}, got {actual}"
        )

    @pytest.mark.property
    @given(role=roles_strategy)
    @settings(max_examples=20)
    def test_administrador_is_superset_of_operador(self, role: str):
        """Administrador permissions SHALL be a superset of Operador permissions.

        **Validates: Requirements 12.4**
        """
        admin_perms = set(RBACMiddleware.ROLE_PERMISSIONS["administrador"])
        operador_perms = set(RBACMiddleware.ROLE_PERMISSIONS["operador"])
        assert operador_perms.issubset(admin_perms), (
            f"Operador has permissions not in Administrador: "
            f"{operador_perms - admin_perms}"
        )

    @pytest.mark.property
    @given(role=unknown_roles_strategy, permission=permissions_strategy)
    @settings(max_examples=30)
    def test_unknown_role_has_no_permissions(
        self, role: str, permission: str
    ):
        """An unknown role SHALL have no permissions granted.

        **Validates: Requirements 12.4**
        """
        assert RBACMiddleware.has_permission(role, permission) is False, (
            f"Unknown role '{role}' should not have permission '{permission}'"
        )

    @pytest.mark.property
    @given(role=roles_strategy)
    @settings(max_examples=10)
    def test_role_permissions_are_non_empty(self, role: str):
        """Every defined role SHALL have at least one permission.

        **Validates: Requirements 12.4**
        """
        permissions = RBACMiddleware.ROLE_PERMISSIONS.get(role, [])
        assert len(permissions) > 0, (
            f"Role '{role}' has no permissions defined"
        )

    @pytest.mark.property
    @given(
        permission=st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz:_",
            min_size=3,
            max_size=20,
        ).filter(lambda p: p not in all_permissions)
    )
    @settings(max_examples=30)
    def test_undefined_permission_denied_for_all_roles(self, permission: str):
        """A permission not defined in any role SHALL be denied for all roles.

        **Validates: Requirements 12.4**
        """
        for role in RBACMiddleware.ROLE_PERMISSIONS:
            assert RBACMiddleware.has_permission(role, permission) is False, (
                f"Undefined permission '{permission}' should be denied "
                f"for role '{role}'"
            )
