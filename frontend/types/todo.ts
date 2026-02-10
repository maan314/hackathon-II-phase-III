// Todo entity types
export interface Todo {
  id: number;
  title: string;
  description: string;
  is_completed: boolean;
  due_date?: string | null;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface TodoCreate {
  title: string;
  description: string;
  is_completed?: boolean;
  due_date?: string | null;
}

export interface TodoUpdate {
  title?: string;
  description?: string;
  is_completed?: boolean;
  due_date?: string | null;
}