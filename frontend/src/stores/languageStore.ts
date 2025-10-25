/**
 * Language Store
 * Manages language preference using Zustand
 */

import { create } from 'zustand';
import i18n from '../locales/i18n';

type Language = 'en' | 'id';

interface LanguageState {
  language: Language;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
}

export const useLanguageStore = create<LanguageState>((set, get) => ({
  language: (localStorage.getItem('language') as Language) || 'en',

  setLanguage: (lang: Language) => {
    i18n.changeLanguage(lang);
    set({ language: lang });
  },

  toggleLanguage: () => {
    const currentLang = get().language;
    const newLang: Language = currentLang === 'en' ? 'id' : 'en';
    get().setLanguage(newLang);
  },
}));
