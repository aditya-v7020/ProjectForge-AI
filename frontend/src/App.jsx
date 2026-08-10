import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/Layout';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import CreateProjectPage from './pages/CreateProjectPage';
import RequirementsPage from './pages/RequirementsPage';
import TechnologySelectionPage from './pages/TechnologySelectionPage';
import ArchitecturePage from './pages/ArchitecturePage';
import TaskBoardPage from './pages/TaskBoardPage';
import TimelinePage from './pages/TimelinePage';
import RiskAnalysisPage from './pages/RiskAnalysisPage';
import BlueprintPage from './pages/BlueprintPage';

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-overlay">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Protected Routes inside App Layout */}
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<DashboardPage />} />

        {/* Create Project Routes */}
        <Route path="/projects/new" element={<CreateProjectPage />} />
        <Route path="/projects/create" element={<CreateProjectPage />} />

        {/* Workflow Stage Routes */}
        <Route path="/projects/:id/requirements" element={<RequirementsPage />} />
        <Route path="/projects/:id/technology-selection" element={<TechnologySelectionPage />} />
        <Route path="/projects/:id/technologies" element={<TechnologySelectionPage />} />
        <Route path="/projects/:id/architecture" element={<ArchitecturePage />} />
        <Route path="/projects/:id/tasks" element={<TaskBoardPage />} />
        <Route path="/projects/:id/timeline" element={<TimelinePage />} />
        <Route path="/projects/:id/risks" element={<RiskAnalysisPage />} />
        <Route path="/projects/:id/blueprint" element={<BlueprintPage />} />
      </Route>

      {/* Wildcard Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
