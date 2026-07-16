import { create } from 'zustand';

interface UiState {
  // Sidebar
  sidebarCollapsed: boolean;
  mobileSidebarOpen: boolean;
  toggleSidebar: () => void;
  setMobileSidebar: (open: boolean) => void;

  // Theme
  theme: 'dark' | 'light';
  toggleTheme: () => void;

  // Command palette
  commandPaletteOpen: boolean;
  setCommandPaletteOpen: (open: boolean) => void;

  // Live connection
  wsConnected: boolean;
  lastUpdated: string | null;
  setConnectionStatus: (connected: boolean, lastUpdated: string) => void;

  // Notification badge count
  notificationCount: number;
  incrementNotifications: () => void;
  clearNotifications: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  sidebarCollapsed: false,
  mobileSidebarOpen: false,
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setMobileSidebar: (open) => set({ mobileSidebarOpen: open }),

  theme: 'dark',
  toggleTheme: () =>
    set((s) => {
      const next = s.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      return { theme: next };
    }),

  commandPaletteOpen: false,
  setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),

  wsConnected: true,
  lastUpdated: null,
  setConnectionStatus: (connected, lastUpdated) => set({ wsConnected: connected, lastUpdated }),

  notificationCount: 0,
  incrementNotifications: () => set((s) => ({ notificationCount: s.notificationCount + 1 })),
  clearNotifications: () => set({ notificationCount: 0 }),
}));
