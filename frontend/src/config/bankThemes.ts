// Configuration des thèmes bancaires
// Mapping par ID de banque (comme dans l'espace agent)
// 17 = CIH Bank
// 18 = Attijariwafa Bank  
// 19 = BCP (Banque Populaire)

// Mapping par code RIB (3 premiers chiffres)
// 007 = Attijariwafa Bank
// 145 = BCP (Banque Populaire)
// 230 = CIH Bank

export interface BankTheme {
  id: string;
  name: string;
  bankId: number;
  ribCode: string;
  primary: string;
  secondary: string;
  accent: string;
  text: string;
  hex: string;
  logo: string;
  gradient: string;
}

// Thèmes par ID de banque (utilisé par l'agent et le bénéficiaire)
export const BANK_THEMES_BY_ID: Record<number, BankTheme> = {
  17: { // CIH
    id: 'cih',
    name: 'CIH Bank',
    bankId: 17,
    ribCode: '230',
    primary: 'bg-cyan-600',
    secondary: 'bg-cyan-800',
    accent: 'bg-cyan-500',
    text: 'text-cyan-700',
    hex: '#06B6D4',
    logo: '/logos/Cih.png',
    gradient: 'from-cyan-500 to-cyan-700',
  },
  18: { // Attijariwafa
    id: 'attijariwafa',
    name: 'Attijariwafa Bank',
    bankId: 18,
    ribCode: '007',
    primary: 'bg-amber-600',
    secondary: 'bg-amber-800',
    accent: 'bg-amber-500',
    text: 'text-amber-700',
    hex: '#d97706',
    logo: '/logos/tijari.png',
    gradient: 'from-amber-500 to-amber-700',
  },
  19: { // Banque Populaire
    id: 'bcp',
    name: 'Banque Populaire',
    bankId: 19,
    ribCode: '145',
    primary: 'bg-orange-300',
    secondary: 'bg-orange-400',
    accent: 'bg-orange-500',
    text: 'text-orange-700',
    hex: '#d27722',
    logo: '/logos/bcp.png',
    gradient: 'from-orange-300 to-orange-500',
  },
};

// Mapping code RIB -> ID banque
export const RIB_TO_BANK_ID: Record<string, number> = {
  '007': 18, // Attijariwafa
  '145': 19, // BCP
  '230': 17, // CIH
};

// Thème par défaut (bleu)
export const DEFAULT_THEME: BankTheme = {
  id: 'default',
  name: 'FraudDetect',
  bankId: 0,
  ribCode: '000',
  primary: 'bg-blue-600',
  secondary: 'bg-blue-700',
  accent: 'bg-blue-500',
  text: 'text-blue-600',
  hex: '#2563eb',
  logo: '/logos/default.png',
  gradient: 'from-blue-500 to-blue-700',
};

/**
 * Retourne le thème correspondant à l'ID de banque
 */
export const getBankThemeById = (bankId: number | null | undefined): BankTheme => {
  if (!bankId) return DEFAULT_THEME;
  return BANK_THEMES_BY_ID[bankId] || DEFAULT_THEME;
};

/**
 * Extrait le code banque du RIB (3 premiers chiffres)
 */
export const extractBankCode = (rib: string | null | undefined): string => {
  if (!rib) return '';
  return rib.substring(0, 3);
};

/**
 * Retourne l'ID de banque à partir du RIB
 */
export const getBankIdFromRib = (rib: string | null | undefined): number | null => {
  const bankCode = extractBankCode(rib);
  return RIB_TO_BANK_ID[bankCode] || null;
};

/**
 * Retourne le thème correspondant au RIB
 */
export const getBankThemeByRib = (rib: string | null | undefined): BankTheme => {
  const bankId = getBankIdFromRib(rib);
  return getBankThemeById(bankId);
};

/**
 * Retourne le nom de la banque basé sur l'ID
 */
export const getBankName = (bankId: number | null | undefined): string => {
  const theme = getBankThemeById(bankId);
  return theme.name;
};

/**
 * Retourne le logo de la banque basé sur l'ID
 */
export const getBankLogo = (bankId: number | null | undefined): string => {
  const theme = getBankThemeById(bankId);
  return theme.logo;
};
