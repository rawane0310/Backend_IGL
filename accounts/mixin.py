from .models import Technician

class CheckUserRoleMixin:
    """
    Mixin pour vérifier si un utilisateur a un rôle parmi une liste donnée et,
    si nécessaire, si son modèle 'Technician' a un rôle parmi une liste donnée.
    """

    def check_user_role(self, user, user_roles=None, technician_roles=None):
        """
        Vérifie si l'utilisateur a un rôle parmi une liste donnée et,
        optionnellement, si son modèle 'Technician' a un rôle parmi une liste donnée.

        Args:
            user: L'objet utilisateur authentifié.
            user_roles: Liste des rôles utilisateur autorisés (ex: ['technicien', 'admin']).
            technician_roles: (Optionnel) Liste des rôles pour le modèle 'Technician' (ex: ['medecin', 'infirmier']).

        Returns:
            bool: True si les rôles correspondent, sinon False.
        """
        # Vérifie si l'utilisateur a un rôle autorisé
        if user_roles and user.role not in user_roles:
            return False

        # Si des rôles de technicien sont spécifiés, vérifie le modèle 'Technician'
        if technician_roles:
            try:
                return user.technician.role in technician_roles  # Vérifie si le rôle du technicien est dans la liste
            except Technician.DoesNotExist:
                return False  # Aucun modèle 'Technician' n'est associé

        # Si tout correspond ou si aucune condition supplémentaire, retourne True
        return True
