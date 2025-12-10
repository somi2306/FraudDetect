# Documentation des Interfaces - FraudDetect

Cette documentation décrit toutes les interfaces et schémas de données utilisés dans le projet FraudDetect, un système de détection de fraude de chèques.

## Table des Matières

1. [Interfaces Backend (Python/Pydantic)](#interfaces-backend-pythonpydantic)
2. [Modèles de Base de Données (SQLAlchemy)](#modèles-de-base-de-données-sqlalchemy)
3. [Interfaces Frontend (TypeScript)](#interfaces-frontend-typescript)
4. [Interfaces des Stores (Zustand)](#interfaces-des-stores-zustand)
5. [Interfaces des Services API](#interfaces-des-services-api)
6. [Interfaces des Composants React](#interfaces-des-composants-react)

---

## Interfaces Backend (Python/Pydantic)

### Schémas Utilisateur (`backend/app/schemas/user.py`)

#### `UserRole`
Énumération des rôles d'utilisateur dans le système.

```python
class UserRole(str, Enum):
    ADMIN = "Admin"
    AGENT = "Agent"
    BENEFICIAIRE = "Bénéficiaire"
```

#### `UserSync`
Schéma pour la synchronisation des données utilisateur avec Clerk.

```python
class UserSync(pydantic.BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    imageUrl: Optional[str] = None
    email: Optional[str] = None
    cin: Optional[str] = None
    rib: Optional[str] = None
```

### Schémas Chèque (`backend/app/schemas/check.py`)

#### `CheckBase`
Schéma de base pour un chèque.

```python
class CheckBase(BaseModel):
    amount: float
    bank_name: str
    check_number: str
    beneficiary_id: UUID
    check_image_url: Optional[str] = None
```

#### `CheckCreate`
Schéma pour la création d'un chèque (hérite de CheckBase).

#### `Check`
Schéma complet d'un chèque avec métadonnées.

```python
class Check(CheckBase):
    id: UUID
    created_at: datetime.datetime
    status: str
```

### Schémas Agent (`backend/app/schemas/agent_schemas.py`)

#### `ChequeSchema`
Représentation d'un chèque pour les agents.

```python
class ChequeSchema(BaseModel):
    id: int
    amount: float
    beneficiaireName: str
    status: str
    date: datetime
```

#### `AgentDashboardData`
Données du tableau de bord d'un agent.

```python
class AgentDashboardData(BaseModel):
    agentName: str
    agentEmail: str
    agentBankId: int
    cheques_meme_banque: List[ChequeSchema]
    cheques_autre_banque: List[ChequeSchema]
```

### Schémas Admin (`backend/app/routes/admin.py`)

#### `BankResponse`
Réponse contenant les informations d'une banque.

```python
class BankResponse(BaseModel):
    id: int
    name: str
```

#### `CreateAgentRequest`
Requête pour créer un nouvel agent.

```python
class CreateAgentRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    personal_email: EmailStr
    password: str
    bank_id: int
```

#### `UpdateAgentRequest`
Requête pour mettre à jour un agent.

```python
class UpdateAgentRequest(BaseModel):
    first_name: str
    last_name: str
```

#### `AgentResponse`
Réponse contenant les informations d'un agent.

```python
class AgentResponse(BaseModel):
    id: int
    clerk_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    bank_name: Optional[str] = None
    is_active: bool
```

#### `BeneficiaryResponse`
Réponse contenant les informations d'un bénéficiaire avec statistiques.

```python
class BeneficiaryResponse(BaseModel):
    id: int
    clerk_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    cin: Optional[str] = None
    rib: Optional[str] = None
    is_active: bool
    total_cheques: int = 0
    rejected_cheques: int = 0
```

### Schémas Chèque Routes (`backend/app/routes/cheques.py`)

#### `ChequeDetail`
Détails d'un chèque lors du dépôt.

```python
class ChequeDetail(BaseModel):
    numero_cheque: str
    montant_cheque: float
```

#### `ChequeResponse`
Réponse complète d'un chèque.

```python
class ChequeResponse(BaseModel):
    id: int
    image_url: str
    date_depot: str
    status: Optional[str]
    banque_nom: Optional[str]
    numero_cheque: Optional[str]
    montant_cheque: Optional[float]
```

#### `ChequeStats`
Statistiques sur les chèques.

```python
class ChequeStats(BaseModel):
    pending: int
    approved: int
    rejected: int
```

#### `ChequeCreateResponse`
Réponse après la création d'un chèque.

```python
class ChequeCreateResponse(BaseModel):
    id: int
    message: str
```

### Schémas Utilisateur Routes (`backend/app/routes/users.py`)

#### `ProfileUpdate`
Schéma pour la mise à jour du profil utilisateur.

```python
class ProfileUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    imageUrl: Optional[str] = None
```

---

## Modèles de Base de Données (SQLAlchemy)

### Modèle Utilisateur (`backend/app/models/user.py`)

#### `User`
Modèle principal pour tous les utilisateurs du système.

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int]  # Clé primaire
    clerk_id: Mapped[str]  # ID Clerk (unique, obligatoire)
    email: Mapped[Optional[str]]
    personal_email: Mapped[Optional[str]]
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    image_url: Mapped[Optional[str]]
    cin: Mapped[Optional[str]]  # Pour bénéficiaires
    rib: Mapped[Optional[str]]  # Pour bénéficiaires
    is_active: Mapped[bool]
    must_reset_password: Mapped[bool]
    role: Mapped[UserRole]  # ADMIN, AGENT, ou BENEFICIAIRE
    bank_id: Mapped[Optional[int]]  # Pour agents
    bank: Mapped[Optional["Bank"]]  # Relation
```

### Modèle Banque (`backend/app/models/bank.py`)

#### `Bank`
Modèle pour les banques.

```python
class Bank(Base):
    __tablename__ = "banks"
    
    id: Mapped[int]  # Clé primaire
    name: Mapped[str]  # Nom unique de la banque
    users: Mapped[List["User"]]  # Relation avec les agents
```

### Modèle Chèque (`backend/app/models/cheque.py`)

#### `Cheque`
Modèle pour les chèques dans le système.

```python
class Cheque(Base):
    __tablename__ = "cheques"
    
    id: Mapped[int]  # Clé primaire
    image_url: Mapped[str]  # URL de l'image du chèque
    status: Mapped[str]  # pending, transmitted, approved, rejected
    date_depot: Mapped[datetime]  # Date de dépôt
    beneficiaire_id: Mapped[int]  # FK vers User (bénéficiaire)
    beneficiaire: relationship("User")
    banque_cible_id: Mapped[int]  # FK vers Bank
    agent_actuel_id: Mapped[int]  # FK vers User (agent)
```

---

## Interfaces Frontend (TypeScript)

### Interfaces Authentification

#### `AuthStore` (`frontend/src/stores/useAuthStore.tsx`)
Store pour l'authentification principale (Clerk).

```typescript
interface AuthStore {
    role: string | null;  // Rôle de l'utilisateur
    bankId: number | null;  // ID de la banque (pour agents)
    isLoading: boolean;
    error: string | null;
    syncUserRole: () => Promise<void>;
    reset: () => void;
}
```

#### `AgentAuthStore` (`frontend/src/stores/useAgentAuthStore.ts`)
Store pour l'authentification des agents (système legacy).

```typescript
interface AgentAuthStore {
    accessToken: string | null;
    user: { id: number; email: string; role: string } | null;
    isLoggedIn: boolean;
    login: (token: string, userId: number, email: string, role: string) => void;
    logout: () => void;
    initializeAuth: () => void;
}
```

### Interfaces Chèque

#### `Cheque` (`frontend/src/pages/beneficiary/BeneficiaryContext.tsx`)
Interface principale pour un chèque côté bénéficiaire.

```typescript
export interface Cheque {
    id: number;
    numero: string;
    montant: number;
    banque: string;
    dateDepot: string;
    statut: string;  // 'en_cours', 'approuve', 'rejete'
    imageUrl?: string;
}
```

#### `Notification`
Notification pour les bénéficiaires.

```typescript
export interface Notification {
    id: number;
    message: string;
    date: string;
    lu: boolean;
}
```

#### `ChequeStats`
Statistiques sur les chèques.

```typescript
export interface ChequeStats {
    pending: number;
    approved: number;
    rejected: number;
}
```

#### `BeneficiaryContextType`
Type du contexte bénéficiaire.

```typescript
interface BeneficiaryContextType {
    checks: Cheque[];
    notifications: Notification[];
    stats: ChequeStats;
    loading: boolean;
    error: string | null;
    refreshChecks: () => Promise<void>;
    addCheck: (check: Partial<Cheque>) => void;
}
```

### Interfaces Agent

#### `Agent` (`frontend/src/pages/admin/ManageAgentsPage.tsx`)
Interface pour un agent dans l'administration.

```typescript
interface Agent {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    bank_name: string;
    is_active: boolean;
}
```

#### `Beneficiary` (`frontend/src/pages/admin/ManageBeneficiariesPage.tsx`)
Interface pour un bénéficiaire dans l'administration.

```typescript
interface Beneficiary {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    cin: string;
    rib: string;
    is_active: boolean;
    total_cheques: number;
    rejected_cheques: number;
}
```

#### `Bank` (`frontend/src/pages/admin/CreateAgentPage.tsx`)
Interface simple pour une banque.

```typescript
interface Bank {
    id: number;
    name: string;
}
```

---

## Interfaces des Services API

### Service Agent (`frontend/src/lib/agentservice.ts`)

#### `BeneficiaireData`
Données d'un bénéficiaire.

```typescript
export interface BeneficiaireData {
    id: number;
    name: string;
    email: string;
}
```

#### `ChequeItem`
Item de chèque avec informations du bénéficiaire.

```typescript
export interface ChequeItem {
    cheque: {
        id: number;
        amount: number;
        status: string;
        date: string;
    };
    beneficiaire: BeneficiaireData;
}
```

#### `AgentDashboardResponse`
Réponse du dashboard agent.

```typescript
export interface AgentDashboardResponse {
    cheques_meme_banque: ChequeItem[];
    cheques_autre_banque: ChequeItem[];
    agentName: string;
    agentEmail: string;
    agentBankId: number;
}
```

### Fonctions API exposées

```typescript
// Récupère les chèques de l'agent connecté
getAgentCheques(): Promise<AgentDashboardResponse>

// Transmet un chèque à un autre agent
transmettreCheque(chequeId: number, agentId: number): Promise<any>

// Récupère les chèques transmis
getChequesTransmis(): Promise<any>

// Récupère les informations de l'agent
getAgentInfo(): Promise<any>

// Récupère les chèques traités
getChequesTraite(): Promise<any>
```

---

## Interfaces des Composants React

### ChequeCard (`frontend/src/components/ChequeCard.tsx`)

#### `ChequeCardProps`
Props du composant carte de chèque.

```typescript
interface ChequeCardProps {
    cheque: Cheque;
    beneficiaire: {
        id: number;
        name: string;
        bankName: string;
    };
    onViewDetails: (cheque: Cheque) => void;
    themeHex: string;
}
```

### ChequeDetailModal (`frontend/src/components/ChequeDetailModal.tsx`)

#### `Cheque`
Interface spécifique pour le modal de détail.

```typescript
export interface Cheque {
    cheque: {
        id: number;
        imageUrl: string;
        status: string;
        date: string;
    };
    beneficiaire: {
        id: number;
        name: string;
        email: string;
    };
}
```

#### `ChequeDetailModalProps`
Props du modal de détail de chèque.

```typescript
interface ChequeDetailModalProps {
    cheque: Cheque | null;
    onClose: () => void;
    isInternal: boolean;  // Banque du chèque = banque de l'agent
    onProcess: (chequeId: number) => void;
    themeHex: string;
    agentId: number;
}
```

### FloatingShape (`frontend/src/components/FloatingShape.tsx`)

#### `FloatingShapeProps`
Props pour les formes flottantes d'animation.

```typescript
interface FloatingShapeProps {
    color: string;
    size: string;
    top: string;
    left: string;
    delay: number;
}
```

### AuthImagePattern (`frontend/src/components/AuthImagePattern.tsx`)

#### `AuthImagePatternProps`
Props pour le motif d'arrière-plan d'authentification.

```typescript
interface AuthImagePatternProps {
    title: string;
    subtitle: string;
}
```

### PasswordStrengthMeter (`frontend/src/components/PasswordStrengthMeter.tsx`)

#### `PasswordCriteriaProps`
Props pour les critères de mot de passe.

```typescript
interface PasswordCriteriaProps {
    password: string;
}
```

#### `PasswordStrengthMeterProps`
Props pour l'indicateur de force du mot de passe.

```typescript
interface PasswordStrengthMeterProps {
    password: string;
}
```

### AgentNavbar (`frontend/src/components/AgentNavbar.tsx`)

#### `AgentNavbarProps`
Props pour la barre de navigation de l'agent.

```typescript
interface AgentNavbarProps {
    themeHex: string;
}
```

### ForgotPassword (`frontend/src/components/ForgotPassword.tsx`)

#### `ForgotPasswordProps`
Props pour le composant de mot de passe oublié.

```typescript
interface ForgotPasswordProps {
    isOpen: boolean;
    onClose: () => void;
}
```

### UploadModal (`frontend/src/pages/beneficiary/components/UploadModal.tsx`)

#### `Bank`
Interface pour sélectionner une banque lors du téléchargement.

```typescript
interface Bank {
    id: number;
    name: string;
}
```

### Toast Hook (`frontend/src/hooks/use-toast.tsx`)

#### `ToasterToast`
Type pour les notifications toast.

```typescript
type ToasterToast = ToastProps & {
    id: string;
    title?: React.ReactNode;
    description?: React.ReactNode;
    action?: ToastActionElement;
}
```

#### `State`
État du système de toast.

```typescript
interface State {
    toasts: ToasterToast[];
}
```

---

## Flux de Données Principaux

### 1. Authentification
- **Frontend**: `useAuthStore` utilise Clerk pour l'authentification
- **Backend**: Vérifie le token JWT Clerk et récupère l'utilisateur via `clerk_id`
- **Route**: `GET /users/me` retourne le profil complet avec rôle

### 2. Gestion des Chèques (Bénéficiaire)
- **Frontend**: `BeneficiaryContext` gère l'état des chèques
- **Backend**: Routes `/cheques/*` pour upload, listing, et statistiques
- **Flux**: Upload → Stockage Supabase → Création en DB → Affectation agent

### 3. Traitement des Chèques (Agent)
- **Frontend**: `AgentDashboardResponse` pour les chèques à traiter
- **Backend**: Routes `/agents/cheques/*` pour récupération et traitement
- **Flux**: Liste chèques → Traitement IA → Mise à jour statut → Notification

### 4. Administration
- **Frontend**: Pages admin pour gérer agents et bénéficiaires
- **Backend**: Routes `/admin/*` avec synchronisation Clerk
- **Flux**: Création utilisateur → Clerk → DB locale → Email notification

---

## Notes de Sécurité

### Authentification
- Tous les endpoints (sauf `/auth/*`) requièrent un token JWT Clerk valide
- Le token est vérifié par la dépendance `get_current_user`
- Les rôles sont vérifiés au niveau de la base de données locale

### Autorisation
- Les agents ne peuvent accéder qu'aux chèques de leur banque ou transmis
- Les bénéficiaires ne voient que leurs propres chèques
- Les admins ont accès complet via les routes `/admin/*`

### Validation des Données
- Pydantic valide toutes les entrées côté backend
- TypeScript assure la cohérence des types côté frontend
- Les images de chèques sont stockées sur Supabase avec URLs signées

---

## Exemples d'Utilisation

### Exemple 1: Créer un nouveau chèque (Frontend)

```typescript
// Dans un composant bénéficiaire
const { addCheck } = useBeneficiary();

const nouveauCheque: Partial<Cheque> = {
    numero: "CHQ123456",
    montant: 5000,
    banque: "Banque Populaire",
    imageUrl: uploadedImageUrl
};

addCheck(nouveauCheque);
```

### Exemple 2: Récupérer les chèques d'un agent (Backend)

```python
# Dans routes/agents.py
@router.get("/cheques/me")
def get_my_cheques(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("user_id")
    agent = db.query(User).filter(
        User.clerk_id == clerk_id,
        User.role == UserRole.AGENT
    ).first()
    
    # Retourne AgentDashboardResponse
    return {
        "cheques_meme_banque": [...],
        "cheques_autre_banque": [...],
        "agentName": agent.first_name,
        "agentEmail": agent.email,
        "agentBankId": agent.bank_id
    }
```

### Exemple 3: Utiliser le store d'authentification (Frontend)

```typescript
// Dans un composant
import { useAuthStore } from '@/stores/useAuthStore';

function MyComponent() {
    const { role, syncUserRole, isLoading } = useAuthStore();
    
    useEffect(() => {
        syncUserRole();
    }, []);
    
    if (role === 'Admin') {
        return <AdminDashboard />;
    } else if (role === 'Agent') {
        return <AgentDashboard />;
    } else {
        return <BeneficiaryDashboard />;
    }
}
```

---

## Changelog des Interfaces

### Version Actuelle
- Intégration complète avec Clerk pour l'authentification
- Support des trois rôles: Admin, Agent, Bénéficiaire
- Système de transmission de chèques entre banques
- Statistiques en temps réel pour les bénéficiaires
- Gestion des agents avec notifications par email

### Améliorations Futures Possibles
- Ajout de webhooks pour les notifications en temps réel
- Support multi-langue pour les interfaces
- Historique détaillé des transactions
- Rapports et analytics avancés
- API publique avec authentification OAuth2

---

## Conclusion

Cette documentation couvre l'ensemble des interfaces utilisées dans le projet FraudDetect. Elle sert de référence pour:
- Les développeurs travaillant sur le frontend ou le backend
- L'intégration de nouvelles fonctionnalités
- La maintenance et le debugging
- La documentation API pour les clients externes

Pour toute question ou suggestion d'amélioration, veuillez contacter l'équipe de développement.
