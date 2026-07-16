import React, { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AppLayout } from '@/components/shell/AppLayout';

// Lazy-loaded pages
const Overview        = lazy(() => import('@/pages/Overview/Overview'));
const Transactions    = lazy(() => import('@/pages/Transactions/Transactions'));
const KnowledgeGraph  = lazy(() => import('@/pages/KnowledgeGraph/KnowledgeGraph'));
const Chaos           = lazy(() => import('@/pages/ChaosEngineering/ChaosEngineering'));
const Customers       = lazy(() => import('@/pages/Customers/Customers'));
const Agents          = lazy(() => import('@/pages/Agents/Agents'));
const TrustCenter     = lazy(() => import('@/pages/TrustCenter/TrustCenter'));
const Explainability  = lazy(() => import('@/pages/Explainability/Explainability'));
const Policies        = lazy(() => import('@/pages/Policies/Policies'));
const HumanReviews    = lazy(() => import('@/pages/HumanReviews/HumanReviews'));
const Incidents       = lazy(() => import('@/pages/Incidents/Incidents'));
const Analytics       = lazy(() => import('@/pages/Analytics/Analytics'));
const Settings        = lazy(() => import('@/pages/Settings/Settings'));

const LoadingFallback = () => (
  <div style={{ padding: 32, display: 'flex', flexDirection: 'column', gap: 12 }}>
    {Array.from({ length: 6 }).map((_, i) => (
      <div key={i} className="skeleton" style={{ height: i === 0 ? 48 : 32, borderRadius: 6 }} />
    ))}
  </div>
);

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true,              element: <Suspense fallback={<LoadingFallback />}><Overview /></Suspense> },
      { path: 'transactions',     element: <Suspense fallback={<LoadingFallback />}><Transactions /></Suspense> },
      { path: 'knowledge-graph',  element: <Suspense fallback={<LoadingFallback />}><KnowledgeGraph /></Suspense> },
      { path: 'chaos',            element: <Suspense fallback={<LoadingFallback />}><Chaos /></Suspense> },
      { path: 'customers',        element: <Suspense fallback={<LoadingFallback />}><Customers /></Suspense> },
      { path: 'agents',           element: <Suspense fallback={<LoadingFallback />}><Agents /></Suspense> },
      { path: 'trust',            element: <Suspense fallback={<LoadingFallback />}><TrustCenter /></Suspense> },
      { path: 'explainability',   element: <Suspense fallback={<LoadingFallback />}><Explainability /></Suspense> },
      { path: 'policies',         element: <Suspense fallback={<LoadingFallback />}><Policies /></Suspense> },
      { path: 'reviews',          element: <Suspense fallback={<LoadingFallback />}><HumanReviews /></Suspense> },
      { path: 'incidents',        element: <Suspense fallback={<LoadingFallback />}><Incidents /></Suspense> },
      { path: 'analytics',        element: <Suspense fallback={<LoadingFallback />}><Analytics /></Suspense> },
      { path: 'settings',         element: <Suspense fallback={<LoadingFallback />}><Settings /></Suspense> },
    ],
  },
]);

export const AppRouter: React.FC = () => <RouterProvider router={router} />;
