import { Routes, Route, Link, Navigate } from 'react-router-dom';
import { useAuth } from '@/auth/useAuth';
import { LoginPage } from '@/auth/LoginPage';
import { ConfigList } from '@/components/configs/ConfigList';
import { ConfigForm } from '@/components/configs/ConfigForm';
import { FilterPanel } from '@/components/dashboard/FilterPanel';
import { DataTable } from '@/components/dashboard/DataTable';
import { SummaryPanel } from '@/components/dashboard/SummaryPanel';
import { ErrorLogViewer } from '@/components/dashboard/ErrorLogViewer';
import { TaskMonitorList } from '@/components/dashboard/TaskMonitorList';
import { TaskMonitorDetail } from '@/components/dashboard/TaskMonitorDetail';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { get } from '@/api/client';
import type { PropertyFilters, PaginatedResponse, PropertyListItem, TaskListItem } from '@/types';

function NavBar() {
  const { user, logout, isAuthenticated } = useAuth();
  if (!isAuthenticated) return null;
  return (
    <nav className="border-b bg-white shadow-sm">
      <div className="container mx-auto flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-6">
          <Link to="/" className="text-lg font-bold text-primary">Scraping Platform</Link>
          <Link to="/configs" className="text-sm hover:text-primary">Configuraciones</Link>
          <Link to="/dashboard" className="text-sm hover:text-primary">Dashboard</Link>
          <Link to="/tasks" className="text-sm hover:text-primary">Tareas</Link>
          <Link to="/errors" className="text-sm hover:text-primary">Errores</Link>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span className="text-muted-foreground">{user?.username} ({user?.role})</span>
          <button onClick={() => logout()} className="rounded-md border px-3 py-1 text-sm hover:bg-muted">Salir</button>
        </div>
      </div>
    </nav>
  );
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <div className="flex min-h-screen items-center justify-center">Cargando...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function ConfigsPage() {
  const [showForm, setShowForm] = useState(false);
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Configuraciones de Scraping</h2>
        <button onClick={() => setShowForm(!showForm)} className="rounded-md bg-primary px-4 py-2 text-sm text-white hover:bg-primary/90">
          {showForm ? 'Cancelar' : '+ Nueva Configuracion'}
        </button>
      </div>
      {showForm && <div className="rounded-md border p-4"><ConfigForm onSuccess={() => setShowForm(false)} onCancel={() => setShowForm(false)} /></div>}
      <ConfigList />
    </div>
  );
}

function DashboardPage() {
  const [filters, setFilters] = useState<PropertyFilters>({});
  const [page, setPage] = useState(1);
  const { data, isLoading } = useQuery({
    queryKey: ['properties', page, filters],
    queryFn: () => get<PaginatedResponse<PropertyListItem>>('/properties', { page, size: 20, ...filters }),
  });
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard de Inmuebles</h2>
      <SummaryPanel />
      <FilterPanel filters={filters} onApply={setFilters} />
      <DataTable data={data} isLoading={isLoading} page={page} onPageChange={setPage} />
    </div>
  );
}

function TasksPage() {
  const [selectedTask, setSelectedTask] = useState<TaskListItem | null>(null);
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Monitor de Tareas</h2>
      {selectedTask ? (
        <div className="space-y-4">
          <button onClick={() => setSelectedTask(null)} className="text-sm text-primary hover:underline">Volver a la lista</button>
          <TaskMonitorDetail taskId={selectedTask.task_id} />
        </div>
      ) : <TaskMonitorList onSelect={setSelectedTask} />}
    </div>
  );
}

function HomePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Plataforma Web Scraping Inmobiliario</h1>
      <p className="text-muted-foreground">Sistema parametrico de extraccion de datos inmobiliarios.</p>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Link to="/configs" className="rounded-lg border p-6 hover:border-primary hover:shadow-md transition-all">
          <h3 className="font-semibold">Configuraciones</h3>
          <p className="mt-1 text-sm text-muted-foreground">Gestionar URLs, profundidad y schedules</p>
        </Link>
        <Link to="/dashboard" className="rounded-lg border p-6 hover:border-primary hover:shadow-md transition-all">
          <h3 className="font-semibold">Dashboard</h3>
          <p className="mt-1 text-sm text-muted-foreground">Consultar y exportar datos inmobiliarios</p>
        </Link>
        <Link to="/tasks" className="rounded-lg border p-6 hover:border-primary hover:shadow-md transition-all">
          <h3 className="font-semibold">Tareas</h3>
          <p className="mt-1 text-sm text-muted-foreground">Monitorear ejecuciones de scraping</p>
        </Link>
        <Link to="/errors" className="rounded-lg border p-6 hover:border-primary hover:shadow-md transition-all">
          <h3 className="font-semibold">Errores</h3>
          <p className="mt-1 text-sm text-muted-foreground">Revisar errores y diagnosticos</p>
        </Link>
      </div>
    </div>
  );
}

function App() {
  return (
    <div className="min-h-screen bg-background font-sans antialiased">
      <NavBar />
      <main className="container mx-auto px-4 py-6">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
          <Route path="/configs" element={<ProtectedRoute><ConfigsPage /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/tasks" element={<ProtectedRoute><TasksPage /></ProtectedRoute>} />
          <Route path="/errors" element={<ProtectedRoute><ErrorsPage /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  );
}

function ErrorsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Log de Errores</h2>
      <ErrorLogViewer />
    </div>
  );
}

export default App;
