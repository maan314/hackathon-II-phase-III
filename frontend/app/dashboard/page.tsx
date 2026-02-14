'use client';

import { useState, useEffect, useMemo } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useActivity } from '@/lib/activity-context';
import { useTheme } from '@/lib/theme-context';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { api } from '@/lib/api-client';
import { Todo } from '@/types/todo';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

type SidebarFilter = 'all' | 'today' | 'upcoming' | 'completed';
type CategoryFilter = 'Work' | 'Personal' | 'Study' | 'Shopping' | 'General' | 'Travelling' | null;
type PriorityFilter = 'High' | 'Medium' | 'Low' | null;
type DateShortcut = 'today' | 'tomorrow' | 'custom';

const CATEGORIES = ['Work', 'Personal', 'Study', 'Shopping', 'General', 'Travelling'] as const;
const PRIORITIES = ['High', 'Medium', 'Low'] as const;

const CATEGORY_COLORS: Record<string, string> = {
  Work: 'bg-blue-500',
  Personal: 'bg-purple-500',
  Study: 'bg-yellow-500',
  Shopping: 'bg-pink-500',
  General: 'bg-gray-500',
  Travelling: 'bg-green-500',
};

const PRIORITY_COLORS: Record<string, string> = {
  High: 'text-red-400 border-red-500/30 bg-red-500/10',
  Medium: 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10',
  Low: 'text-green-400 border-green-500/30 bg-green-500/10',
};

function getToday() {
  return new Date().toISOString().split('T')[0];
}

function getTomorrow() {
  const d = new Date();
  d.setDate(d.getDate() + 1);
  return d.toISOString().split('T')[0];
}

function isToday(dateStr: string | null | undefined) {
  if (!dateStr) return false;
  return new Date(dateStr).toDateString() === new Date().toDateString();
}

function isUpcoming(dateStr: string | null | undefined) {
  if (!dateStr) return false;
  const d = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return d >= today;
}

export default function DashboardPage() {
  const { user, isLoading: authLoading, signOut } = useAuth();
  const { logActivity } = useActivity();
  const { theme, toggleTheme } = useTheme();
  const router = useRouter();

  // Task state
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New task form
  const [newTitle, setNewTitle] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newDueDate, setNewDueDate] = useState('');
  const [newCategory, setNewCategory] = useState<string>('General');
  const [newPriority, setNewPriority] = useState<string>('Medium');
  const [dateShortcut, setDateShortcut] = useState<DateShortcut>('today');
  const [showDescription, setShowDescription] = useState(false);

  // Edit state
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [editForm, setEditForm] = useState({ title: '', description: '', due_date: '' });

  // Filters
  const [sidebarFilter, setSidebarFilter] = useState<SidebarFilter>('all');
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>(null);
  const [priorityFilter, setPriorityFilter] = useState<PriorityFilter>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Sidebar collapse on mobile
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Fetch todos
  const fetchTodos = async () => {
    try {
      setLoading(true);
      const response = await api.get<Todo[]>('/todos');
      setTodos(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch todos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) fetchTodos();
  }, [user]);

  // Set date based on shortcut
  useEffect(() => {
    if (dateShortcut === 'today') setNewDueDate(getToday());
    else if (dateShortcut === 'tomorrow') setNewDueDate(getTomorrow());
  }, [dateShortcut]);

  // Filtered todos
  const filteredTodos = useMemo(() => {
    let filtered = [...todos];

    // Sidebar filter
    if (sidebarFilter === 'today') {
      filtered = filtered.filter(t => isToday(t.due_date));
    } else if (sidebarFilter === 'upcoming') {
      filtered = filtered.filter(t => isUpcoming(t.due_date) && !t.is_completed);
    } else if (sidebarFilter === 'completed') {
      filtered = filtered.filter(t => t.is_completed);
    }

    // Category filter (stored in description as [Category: X])
    if (categoryFilter) {
      filtered = filtered.filter(t =>
        t.description?.includes(`[Category: ${categoryFilter}]`)
      );
    }

    // Priority filter (stored in description as [Priority: X])
    if (priorityFilter) {
      filtered = filtered.filter(t =>
        t.description?.includes(`[Priority: ${priorityFilter}]`)
      );
    }

    // Search
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(t =>
        t.title.toLowerCase().includes(q) ||
        t.description?.toLowerCase().includes(q)
      );
    }

    return filtered;
  }, [todos, sidebarFilter, categoryFilter, priorityFilter, searchQuery]);

  // Task counts
  const counts = useMemo(() => ({
    all: todos.length,
    today: todos.filter(t => isToday(t.due_date)).length,
    upcoming: todos.filter(t => isUpcoming(t.due_date) && !t.is_completed).length,
    completed: todos.filter(t => t.is_completed).length,
  }), [todos]);

  // Create todo
  const handleCreateTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) { setError('Title is required'); return; }

    // Embed category and priority in description
    const metaTags = `[Category: ${newCategory}] [Priority: ${newPriority}]`;
    const fullDescription = newDescription
      ? `${newDescription}\n${metaTags}`
      : metaTags;

    try {
      const response = await api.post<Todo>('/todos', {
        title: newTitle,
        description: fullDescription,
        due_date: newDueDate || null,
        is_completed: false,
      });
      setTodos([response.data, ...todos]);
      setNewTitle('');
      setNewDescription('');
      setNewDueDate(getToday());
      setDateShortcut('today');
      setNewCategory('General');
      setNewPriority('Medium');
      setShowDescription(false);
      setError(null);
      logActivity({ action: `Created "${response.data.title}"`, type: 'task-created' });
    } catch (err: any) {
      setError(err.message || 'Failed to create todo');
    }
  };

  // Toggle completion
  const handleToggleTodo = async (id: number, currentStatus: boolean) => {
    const todo = todos.find(t => t.id === id);
    const newStatus = !currentStatus;
    setTodos(prev => prev.map(t => t.id === id ? { ...t, is_completed: newStatus } : t));
    try {
      const response = await api.put<Todo>(`/todos/${id}`, {
        status: newStatus ? 'completed' : 'pending',
      });
      setTodos(prev => prev.map(t => t.id === id ? response.data : t));
      logActivity({
        action: `${newStatus ? 'Completed' : 'Reopened'} "${todo?.title || 'a task'}"`,
        type: newStatus ? 'task-completed' : 'task-edited',
      });
    } catch (err: any) {
      setTodos(prev => prev.map(t => t.id === id ? { ...t, is_completed: currentStatus } : t));
      setError(err.message || 'Failed to update todo');
    }
  };

  // Delete todo
  const handleDeleteTodo = async (id: number) => {
    const todo = todos.find(t => t.id === id);
    try {
      await api.delete(`/todos/${id}`);
      setTodos(prev => prev.filter(t => t.id !== id));
      logActivity({ action: `Deleted "${todo?.title || 'a task'}"`, type: 'task-deleted' });
    } catch (err: any) {
      setError(err.message || 'Failed to delete todo');
    }
  };

  // Edit todo
  const startEditing = (todo: Todo) => {
    setEditingTodo(todo);
    setEditForm({
      title: todo.title,
      description: todo.description?.replace(/\n?\[Category: \w+\] \[Priority: \w+\]/, '') || '',
      due_date: todo.due_date ? new Date(todo.due_date).toISOString().split('T')[0] : '',
    });
  };
  const cancelEditing = () => { setEditingTodo(null); setEditForm({ title: '', description: '', due_date: '' }); };
  const saveEditedTodo = async (id: number) => {
    if (!editForm.title.trim()) { setError('Title is required'); return; }
    try {
      const response = await api.put<Todo>(`/todos/${id}`, {
        title: editForm.title,
        description: editForm.description,
        due_date: editForm.due_date || null,
      });
      setTodos(prev => prev.map(t => t.id === id ? response.data : t));
      setEditingTodo(null);
      setEditForm({ title: '', description: '', due_date: '' });
      logActivity({ action: `Edited "${response.data.title}"`, type: 'task-edited' });
    } catch (err: any) {
      setError(err.message || 'Failed to update todo');
    }
  };

  // Extract category/priority from description
  const getCategory = (desc: string | undefined) => {
    const match = desc?.match(/\[Category: (\w+)\]/);
    return match ? match[1] : null;
  };
  const getPriority = (desc: string | undefined) => {
    const match = desc?.match(/\[Priority: (\w+)\]/);
    return match ? match[1] : null;
  };
  const cleanDescription = (desc: string | undefined) => {
    if (!desc) return '';
    return desc.replace(/\n?\[Category: \w+\] \[Priority: \w+\]/, '').trim();
  };

  // Auth guard
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-black">
        <div className="flex items-center gap-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
          <span className="text-gray-400 text-lg">Loading...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    router.push('/signin');
    return null;
  }

  const handleSignOut = () => { signOut(); router.push('/signin'); };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white flex flex-col">
      {/* ===== NAVBAR ===== */}
      <nav className="h-16 border-b border-gray-700/50 bg-gray-900/80 backdrop-blur-md flex items-center justify-between px-4 md:px-6 sticky top-0 z-50">
        <div className="flex items-center gap-4">
          {/* Mobile sidebar toggle */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-800 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          {/* App Name */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent hidden sm:inline">
              Todo Management App
            </span>
          </Link>
        </div>

        {/* Search Bar - Desktop */}
        <div className="hidden md:flex flex-1 max-w-md mx-6">
          <div className="relative w-full">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-gray-800/60 border border-gray-700/50 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 transition-all"
            />
          </div>
        </div>

        {/* User info + actions */}
        <div className="flex items-center gap-3">
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-gray-800 transition-colors"
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? (
              <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            )}
          </button>

          {/* User avatar & name */}
          <div className="hidden sm:flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500 to-purple-600 flex items-center justify-center text-xs font-bold">
              {(user?.first_name?.charAt(0) || '')}{(user?.last_name?.charAt(0) || '')}
            </div>
            <span className="text-sm text-gray-300">
              {user?.first_name} {user?.last_name}
            </span>
          </div>

          {/* Sign Out */}
          <Button
            onClick={handleSignOut}
            variant="outline"
            size="sm"
            className="border-red-500/40 text-red-400 hover:bg-red-500/10 hover:border-red-500/60 text-xs"
          >
            Sign Out
          </Button>
        </div>
      </nav>

      {/* Mobile search */}
      <div className="md:hidden px-4 py-2 bg-gray-900/50 border-b border-gray-700/30">
        <div className="relative w-full">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg bg-gray-800/60 border border-gray-700/50 text-white placeholder-gray-500 text-sm focus:outline-none focus:border-cyan-500/50 transition-all"
          />
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* ===== SIDEBAR ===== */}
        {/* Mobile overlay */}
        {sidebarOpen && (
          <div className="fixed inset-0 bg-black/50 z-30 md:hidden" onClick={() => setSidebarOpen(false)} />
        )}

        <aside className={`
          fixed md:sticky top-16 left-0 h-[calc(100vh-4rem)] w-64 bg-gray-900/95 md:bg-gray-900/50 backdrop-blur-md
          border-r border-gray-700/30 flex-shrink-0 overflow-y-auto z-40
          transition-transform duration-300
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}>
          <div className="p-4 space-y-6">
            {/* Task Filters */}
            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">Tasks</h3>
              <div className="space-y-1">
                {[
                  { key: 'all' as SidebarFilter, label: 'All Tasks', icon: 'M4 6h16M4 10h16M4 14h16M4 18h16', count: counts.all },
                  { key: 'today' as SidebarFilter, label: 'Today', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z', count: counts.today },
                  { key: 'upcoming' as SidebarFilter, label: 'Upcoming', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z', count: counts.upcoming },
                  { key: 'completed' as SidebarFilter, label: 'Completed', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', count: counts.completed },
                ].map(item => (
                  <button
                    key={item.key}
                    onClick={() => { setSidebarFilter(item.key); setCategoryFilter(null); setPriorityFilter(null); setSidebarOpen(false); }}
                    className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                      sidebarFilter === item.key && !categoryFilter && !priorityFilter
                        ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30'
                        : 'text-gray-400 hover:bg-gray-800/60 hover:text-gray-200 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                      </svg>
                      <span>{item.label}</span>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      sidebarFilter === item.key && !categoryFilter && !priorityFilter
                        ? 'bg-cyan-500/20 text-cyan-400'
                        : 'bg-gray-800 text-gray-500'
                    }`}>
                      {item.count}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-gray-700/30" />

            {/* Categories */}
            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">Categories</h3>
              <div className="space-y-1">
                {CATEGORIES.map(cat => {
                  const catCount = todos.filter(t => t.description?.includes(`[Category: ${cat}]`)).length;
                  return (
                    <button
                      key={cat}
                      onClick={() => {
                        setCategoryFilter(categoryFilter === cat ? null : cat);
                        setPriorityFilter(null);
                        setSidebarFilter('all');
                        setSidebarOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                        categoryFilter === cat
                          ? 'bg-purple-500/15 text-purple-400 border border-purple-500/30'
                          : 'text-gray-400 hover:bg-gray-800/60 hover:text-gray-200 border border-transparent'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${CATEGORY_COLORS[cat]}`} />
                        <span>{cat}</span>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        categoryFilter === cat
                          ? 'bg-purple-500/20 text-purple-400'
                          : 'bg-gray-800 text-gray-500'
                      }`}>
                        {catCount}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-gray-700/30" />

            {/* Priorities */}
            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">Priorities</h3>
              <div className="space-y-1">
                {PRIORITIES.map(pri => {
                  const priCount = todos.filter(t => t.description?.includes(`[Priority: ${pri}]`)).length;
                  const colors = pri === 'High' ? 'bg-red-500' : pri === 'Medium' ? 'bg-yellow-500' : 'bg-green-500';
                  return (
                    <button
                      key={pri}
                      onClick={() => {
                        setPriorityFilter(priorityFilter === pri ? null : pri);
                        setCategoryFilter(null);
                        setSidebarFilter('all');
                        setSidebarOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                        priorityFilter === pri
                          ? 'bg-pink-500/15 text-pink-400 border border-pink-500/30'
                          : 'text-gray-400 hover:bg-gray-800/60 hover:text-gray-200 border border-transparent'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${colors}`} />
                        <span>{pri}</span>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        priorityFilter === pri
                          ? 'bg-pink-500/20 text-pink-400'
                          : 'bg-gray-800 text-gray-500'
                      }`}>
                        {priCount}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-gray-700/30" />

            {/* Quick links */}
            <div>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-2">Quick Links</h3>
              <div className="space-y-1">
                <Link
                  href="/chat"
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-400 hover:bg-gray-800/60 hover:text-gray-200 transition-all"
                  onClick={() => setSidebarOpen(false)}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <span>AI Chat</span>
                </Link>
                <Link
                  href="/profile"
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-400 hover:bg-gray-800/60 hover:text-gray-200 transition-all"
                  onClick={() => setSidebarOpen(false)}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <span>Profile</span>
                </Link>
                <Link
                  href="/settings"
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-400 hover:bg-gray-800/60 hover:text-gray-200 transition-all"
                  onClick={() => setSidebarOpen(false)}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span>Settings</span>
                </Link>
              </div>
            </div>
          </div>
        </aside>

        {/* ===== MAIN CONTENT ===== */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
          {/* Header */}
          <div className="mb-6">
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              {categoryFilter ? `${categoryFilter} Tasks` :
               priorityFilter ? `${priorityFilter} Priority` :
               sidebarFilter === 'all' ? 'All Tasks' :
               sidebarFilter === 'today' ? "Today's Tasks" :
               sidebarFilter === 'upcoming' ? 'Upcoming Tasks' :
               'Completed Tasks'}
            </h1>
            <p className="text-gray-400 mt-1 text-sm">
              {filteredTodos.length} task{filteredTodos.length !== 1 ? 's' : ''}
              {searchQuery && ` matching "${searchQuery}"`}
            </p>
          </div>

          {/* Error */}
          {error && (
            <div className="mb-4 rounded-lg bg-red-500/20 p-3 border border-red-500/30 flex items-center justify-between">
              <p className="text-sm text-red-300">{error}</p>
              <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}

          {/* ===== QUICK ACTIONS ===== */}
          <div className="mb-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Link
              href="/chat"
              className="flex items-center gap-3 p-4 rounded-xl border border-purple-500/20 bg-gray-800/30 backdrop-blur-sm hover:border-purple-500/40 hover:bg-gray-800/50 transition-all duration-200 group"
            >
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center group-hover:from-purple-500/30 group-hover:to-pink-500/30 transition-all">
                <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-white">AI Chat Assistant</p>
                <p className="text-xs text-gray-500">Manage tasks with AI</p>
              </div>
            </Link>

            <Link
              href="/profile"
              className="flex items-center gap-3 p-4 rounded-xl border border-pink-500/20 bg-gray-800/30 backdrop-blur-sm hover:border-pink-500/40 hover:bg-gray-800/50 transition-all duration-200 group"
            >
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-pink-500/20 to-orange-500/20 flex items-center justify-center group-hover:from-pink-500/30 group-hover:to-orange-500/30 transition-all">
                <svg className="w-5 h-5 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-white">Profile</p>
                <p className="text-xs text-gray-500">View your profile</p>
              </div>
            </Link>
          </div>

          {/* ===== ADD TASK FORM ===== */}
          <form onSubmit={handleCreateTodo} className="mb-6 rounded-xl border border-cyan-500/20 bg-gray-800/30 backdrop-blur-sm p-4">
            <div className="flex gap-3 mb-3">
              <div className="flex-1">
                <Input
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="What needs to be done?"
                  className="h-11 bg-gray-800/50 border-gray-700/50 text-white placeholder-gray-500 focus:border-cyan-500/50"
                />
              </div>
              <Button
                type="submit"
                className="h-11 px-6 bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white font-medium"
              >
                <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Task
              </Button>
            </div>

            {/* Task Options Row */}
            <div className="flex flex-wrap items-center gap-2">
              {/* Date shortcuts */}
              <div className="flex items-center gap-1 bg-gray-800/50 rounded-lg p-1 border border-gray-700/30">
                <button
                  type="button"
                  onClick={() => setDateShortcut('today')}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    dateShortcut === 'today'
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                      : 'text-gray-400 hover:text-gray-300 border border-transparent'
                  }`}
                >
                  Today
                </button>
                <button
                  type="button"
                  onClick={() => setDateShortcut('tomorrow')}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    dateShortcut === 'tomorrow'
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                      : 'text-gray-400 hover:text-gray-300 border border-transparent'
                  }`}
                >
                  Tomorrow
                </button>
                <button
                  type="button"
                  onClick={() => setDateShortcut('custom')}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    dateShortcut === 'custom'
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                      : 'text-gray-400 hover:text-gray-300 border border-transparent'
                  }`}
                >
                  Pick Date
                </button>
              </div>

              {dateShortcut === 'custom' && (
                <input
                  type="date"
                  value={newDueDate}
                  onChange={(e) => setNewDueDate(e.target.value)}
                  className="h-8 px-3 text-xs rounded-lg bg-gray-800/50 border border-gray-700/30 text-white focus:outline-none focus:border-cyan-500/50"
                />
              )}

              {/* Category selector */}
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="h-8 px-3 text-xs rounded-lg bg-gray-800/50 border border-gray-700/30 text-gray-300 focus:outline-none focus:border-cyan-500/50 appearance-none cursor-pointer"
              >
                {CATEGORIES.map(cat => (
                  <option key={cat} value={cat} className="bg-gray-800">{cat}</option>
                ))}
              </select>

              {/* Priority selector */}
              <select
                value={newPriority}
                onChange={(e) => setNewPriority(e.target.value)}
                className="h-8 px-3 text-xs rounded-lg bg-gray-800/50 border border-gray-700/30 text-gray-300 focus:outline-none focus:border-cyan-500/50 appearance-none cursor-pointer"
              >
                {PRIORITIES.map(pri => (
                  <option key={pri} value={pri} className="bg-gray-800">{pri}</option>
                ))}
              </select>

              {/* Toggle description */}
              <button
                type="button"
                onClick={() => setShowDescription(!showDescription)}
                className="h-8 px-3 text-xs rounded-lg bg-gray-800/50 border border-gray-700/30 text-gray-400 hover:text-gray-300 transition-colors"
              >
                {showDescription ? 'Hide' : '+ Note'}
              </button>
            </div>

            {/* Description textarea */}
            {showDescription && (
              <div className="mt-3">
                <Textarea
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Add a note..."
                  rows={2}
                  className="bg-gray-800/50 border-gray-700/50 text-white placeholder-gray-500 text-sm"
                />
              </div>
            )}
          </form>

          {/* ===== TASK LIST ===== */}
          {loading ? (
            <div className="flex justify-center items-center py-16">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
              <span className="ml-3 text-gray-400">Loading tasks...</span>
            </div>
          ) : filteredTodos.length === 0 ? (
            <div className="text-center py-16 rounded-xl border border-gray-700/30 bg-gray-800/20">
              <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <p className="text-gray-400 text-lg mb-1">No tasks found</p>
              <p className="text-gray-500 text-sm">
                {searchQuery ? 'Try a different search term' : 'Add your first task above!'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredTodos.map((todo) => {
                const category = getCategory(todo.description);
                const priority = getPriority(todo.description);
                const desc = cleanDescription(todo.description);

                return (
                  <div
                    key={todo.id}
                    className={`group rounded-xl border transition-all duration-200 hover:shadow-lg ${
                      todo.is_completed
                        ? 'bg-gray-800/20 border-green-500/20 hover:shadow-green-500/5'
                        : 'bg-gray-800/30 border-gray-700/30 hover:border-cyan-500/30 hover:shadow-cyan-500/5'
                    }`}
                  >
                    {editingTodo?.id === todo.id ? (
                      /* Edit mode */
                      <div className="p-4 space-y-3">
                        <Input
                          value={editForm.title}
                          onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                          placeholder="Task title"
                          className="h-10 bg-gray-800/50 border-gray-700/50 text-white"
                        />
                        <Textarea
                          value={editForm.description}
                          onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                          placeholder="Description..."
                          rows={2}
                          className="bg-gray-800/50 border-gray-700/50 text-white text-sm"
                        />
                        <Input
                          type="date"
                          value={editForm.due_date}
                          onChange={(e) => setEditForm({...editForm, due_date: e.target.value})}
                          className="h-10 bg-gray-800/50 border-gray-700/50 text-white"
                        />
                        <div className="flex gap-2">
                          <Button onClick={() => saveEditedTodo(todo.id)} size="sm" className="bg-green-600 hover:bg-green-500 text-white text-xs">
                            Save
                          </Button>
                          <Button onClick={cancelEditing} variant="outline" size="sm" className="border-gray-600 text-gray-300 hover:bg-gray-700 text-xs">
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      /* View mode */
                      <div className="p-4 flex items-start gap-3">
                        <Checkbox
                          checked={todo.is_completed}
                          onCheckedChange={() => handleToggleTodo(todo.id, todo.is_completed)}
                          className={`mt-1 ${todo.is_completed ? 'border-green-500 data-[state=checked]:bg-green-500 data-[state=checked]:border-green-500' : 'border-gray-600 data-[state=checked]:bg-cyan-500 data-[state=checked]:border-cyan-500'}`}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap mb-1">
                            <h3 className={`font-medium ${todo.is_completed ? 'line-through text-gray-500' : 'text-white'}`}>
                              {todo.title}
                            </h3>
                            {category && (
                              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${
                                todo.is_completed ? 'opacity-50' : ''
                              }`}>
                                <span className={`w-2 h-2 rounded-full ${CATEGORY_COLORS[category] || 'bg-gray-500'}`} />
                                <span className="text-gray-400">{category}</span>
                              </span>
                            )}
                            {priority && (
                              <span className={`px-2 py-0.5 rounded-full text-xs border ${PRIORITY_COLORS[priority] || ''} ${
                                todo.is_completed ? 'opacity-50' : ''
                              }`}>
                                {priority}
                              </span>
                            )}
                            {todo.is_completed && (
                              <span className="px-2 py-0.5 text-xs bg-green-500/20 text-green-400 rounded-full border border-green-500/30">
                                Done
                              </span>
                            )}
                          </div>
                          {desc && (
                            <p className={`text-sm ${todo.is_completed ? 'line-through text-gray-600' : 'text-gray-400'}`}>
                              {desc}
                            </p>
                          )}
                          <div className="mt-2 flex items-center gap-3 text-xs text-gray-500">
                            {todo.due_date && (
                              <span className={`flex items-center gap-1 ${
                                !todo.is_completed && new Date(todo.due_date) < new Date()
                                  ? 'text-red-400'
                                  : isToday(todo.due_date)
                                    ? 'text-cyan-400'
                                    : ''
                              }`}>
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                {!todo.is_completed && new Date(todo.due_date) < new Date()
                                  ? `Overdue: ${new Date(todo.due_date).toLocaleDateString()}`
                                  : isToday(todo.due_date)
                                    ? 'Today'
                                    : new Date(todo.due_date).toLocaleDateString()
                                }
                              </span>
                            )}
                            <span>Created {new Date(todo.created_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => startEditing(todo)}
                            className="p-1.5 rounded-lg hover:bg-gray-700/50 text-gray-400 hover:text-cyan-400 transition-colors"
                            title="Edit"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                          <button
                            onClick={() => handleDeleteTodo(todo.id)}
                            className="p-1.5 rounded-lg hover:bg-red-500/10 text-gray-400 hover:text-red-400 transition-colors"
                            title="Delete"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Footer - merged transparently */}
          <div className="mt-8 pb-2 text-center text-xs text-gray-600">
            <p>
              Created by{' '}
              <span className="bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent font-semibold">
                Muhammad Usman
              </span>
              {' '}&copy; 2026
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
