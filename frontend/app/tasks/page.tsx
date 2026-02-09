'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { getToken } from '@/lib/auth-utils';
import { api } from '@/lib/api-client';
import { Todo } from '@/types/todo';
import { useRouter } from 'next/navigation';
import { useActivity } from '@/lib/activity-context';

export default function TasksPage() {
  const router = useRouter();
  const { logActivity } = useActivity();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodo, setNewTodo] = useState({ title: '', description: '' });
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [editForm, setEditForm] = useState({ title: '', description: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch todos from the backend
  const fetchTodos = async () => {
    try {
      setLoading(true);
      const response = await api.get<Todo[]>('/todos');
      setTodos(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch todos');
      console.error('Error fetching todos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  // Create a new todo
  const handleCreateTodo = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newTodo.title.trim()) {
      setError('Title is required');
      return;
    }

    try {
      const response = await api.post<Todo>('/todos', {
        title: newTodo.title,
        description: newTodo.description,
        is_completed: false
      });

      setTodos([response.data, ...todos]);
      setNewTodo({ title: '', description: '' });
      setError(null);

      // Log activity
      logActivity({
        action: `Created "${response.data.title}"`,
        type: 'task-created'
      });
    } catch (err: any) {
      setError(err.message || 'Failed to create todo');
      console.error('Error creating todo:', err);
    }
  };

  // Toggle todo completion status - FIXED VERSION
  const handleToggleTodo = async (id: number, currentStatus: boolean) => {
    const todo = todos.find(t => t.id === id);
    const newStatus = !currentStatus;

    // Optimistically update UI immediately
    setTodos(prevTodos => prevTodos.map(t =>
      t.id === id ? { ...t, is_completed: newStatus } : t
    ));

    try {
      const response = await api.put<Todo>(`/todos/${id}`, {
        is_completed: newStatus
      });

      // Update with server response to ensure sync
      setTodos(prevTodos => prevTodos.map(t =>
        t.id === id ? response.data : t
      ));
      setError(null);

      // Log activity
      logActivity({
        action: `${newStatus ? 'Completed' : 'Reopened'} "${todo?.title || 'a task'}"`,
        type: newStatus ? 'task-completed' : 'task-edited'
      });
    } catch (err: any) {
      // Rollback on error
      setTodos(prevTodos => prevTodos.map(t =>
        t.id === id ? { ...t, is_completed: currentStatus } : t
      ));
      setError(err.message || 'Failed to update todo');
      console.error('Error updating todo:', err);
    }
  };

  // Delete a todo
  const handleDeleteTodo = async (id: number) => {
    const todo = todos.find(t => t.id === id);

    try {
      await api.delete(`/todos/${id}`);
      setTodos(prevTodos => prevTodos.filter(t => t.id !== id));
      setError(null);

      // Log activity
      logActivity({
        action: `Deleted "${todo?.title || 'a task'}"`,
        type: 'task-deleted'
      });
    } catch (err: any) {
      setError(err.message || 'Failed to delete todo');
      console.error('Error deleting todo:', err);
    }
  };

  // Start editing a todo
  const startEditing = (todo: Todo) => {
    setEditingTodo(todo);
    setEditForm({ title: todo.title, description: todo.description });
  };

  // Cancel editing
  const cancelEditing = () => {
    setEditingTodo(null);
    setEditForm({ title: '', description: '' });
  };

  // Save edited todo
  const saveEditedTodo = async (id: number) => {
    if (!editForm.title.trim()) {
      setError('Title is required');
      return;
    }

    try {
      const response = await api.put<Todo>(`/todos/${id}`, {
        title: editForm.title,
        description: editForm.description,
        is_completed: editingTodo?.is_completed || false
      });

      setTodos(prevTodos => prevTodos.map(todo =>
        todo.id === id ? response.data : todo
      ));

      setEditingTodo(null);
      setEditForm({ title: '', description: '' });
      setError(null);

      // Log activity
      logActivity({
        action: `Edited "${response.data.title}"`,
        type: 'task-edited'
      });
    } catch (err: any) {
      setError(err.message || 'Failed to update todo');
      console.error('Error updating todo:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white p-4">
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              My Tasks
            </h1>
            <p className="text-gray-400 mt-2">Manage your tasks efficiently</p>
          </div>
          <Button
            onClick={() => router.push('/dashboard')}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white"
          >
            Back to Dashboard
          </Button>
        </div>

        {error && (
          <div className="mb-6 rounded-lg bg-red-500/20 p-4 border border-red-500/30">
            <p className="text-sm text-red-300 font-medium">{error}</p>
          </div>
        )}

        {/* Add New Todo Form */}
        <form onSubmit={handleCreateTodo} className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div className="md:col-span-2">
              <Input
                value={newTodo.title}
                onChange={(e) => setNewTodo({...newTodo, title: e.target.value})}
                placeholder="Task title..."
                className="h-12 bg-gray-800/50 border-cyan-500/30 text-white placeholder-gray-400"
              />
            </div>
            <div className="md:col-span-1">
              <Button
                type="submit"
                className="w-full h-12 bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white"
              >
                Add Task
              </Button>
            </div>
          </div>
          <Textarea
            value={newTodo.description}
            onChange={(e) => setNewTodo({...newTodo, description: e.target.value})}
            placeholder="Task description (optional)..."
            rows={2}
            className="bg-gray-800/50 border-cyan-500/30 text-white placeholder-gray-400"
          />
        </form>

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center items-center py-16">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
            <span className="ml-3 text-gray-400">Loading tasks...</span>
          </div>
        )}

        {/* Empty State */}
        {!loading && todos.length === 0 && (
          <div className="text-center py-16 rounded-2xl border border-cyan-500/20 bg-gradient-to-br from-gray-800/30 to-gray-900/30 backdrop-blur-sm p-8">
            <p className="text-gray-400 text-lg">No tasks yet. Add your first task above!</p>
          </div>
        )}

        {/* Todos List */}
        {!loading && todos.length > 0 && (
          <div className="space-y-4">
            {todos.map((todo) => (
              <div
                key={todo.id}
                className={`p-6 rounded-2xl border ${
                  todo.is_completed
                    ? 'bg-gradient-to-r from-green-900/20 to-emerald-900/20 border-green-500/30'
                    : 'bg-gradient-to-r from-gray-800/50 to-gray-900/50 border-cyan-500/20'
                } backdrop-blur-sm`}
              >
                {editingTodo?.id === todo.id ? (
                  // Edit mode
                  <div className="space-y-4">
                    <Input
                      value={editForm.title}
                      onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                      className="h-10 bg-gray-800/50 border-cyan-500/30 text-white placeholder-gray-400"
                    />
                    <Textarea
                      value={editForm.description}
                      onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                      placeholder="Task description (optional)..."
                      rows={2}
                      className="bg-gray-800/50 border-cyan-500/30 text-white placeholder-gray-400"
                    />
                    <div className="flex gap-2">
                      <Button
                        onClick={() => saveEditedTodo(todo.id)}
                        className="bg-green-600 hover:bg-green-500 text-white"
                      >
                        Save
                      </Button>
                      <Button
                        onClick={cancelEditing}
                        variant="outline"
                        className="border-gray-600 text-gray-300 hover:bg-gray-700"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                ) : (
                  // View mode
                  <>
                    <div className="flex items-start gap-4">
                      <Checkbox
                        checked={todo.is_completed}
                        onCheckedChange={() => handleToggleTodo(todo.id, todo.is_completed)}
                        className={`mt-1 ${todo.is_completed ? 'border-green-500' : 'border-cyan-500'} data-[state=checked]:bg-cyan-500 data-[state=checked]:border-cyan-500`}
                      />
                      <div className="flex-1">
                        <h3 className={`font-medium text-lg ${todo.is_completed ? 'line-through text-gray-500' : 'text-white'}`}>
                          {todo.title}
                        </h3>
                        {todo.description && (
                          <p className={`mt-2 text-sm ${todo.is_completed ? 'line-through text-gray-500' : 'text-gray-300'}`}>
                            {todo.description}
                          </p>
                        )}
                        <p className="mt-3 text-xs text-gray-500">
                          Created: {new Date(todo.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          onClick={() => startEditing(todo)}
                          variant="outline"
                          size="sm"
                          className="h-8 border-cyan-500 text-cyan-400 hover:bg-cyan-500/10"
                        >
                          Edit
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteTodo(todo.id)}
                          className="h-8 bg-red-600/80 hover:bg-red-600 text-white"
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}