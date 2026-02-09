'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

export type ActivityType = 'task-created' | 'task-completed' | 'task-edited' | 'task-deleted' | 'signed-in' | 'signed-out' | 'profile-updated';

export interface Activity {
  id: number;
  action: string;
  timestamp: string;
  type: ActivityType;
}

interface ActivityContextType {
  activities: Activity[];
  logActivity: (activity: Omit<Activity, 'id' | 'timestamp'>) => void;
  clearActivities: () => void;
}

const ActivityContext = createContext<ActivityContextType | undefined>(undefined);

interface ActivityProviderProps {
  children: ReactNode;
}

export function ActivityProvider({ children }: ActivityProviderProps) {
  const [activities, setActivities] = useState<Activity[]>([]);

  const logActivity = (activityData: Omit<Activity, 'id' | 'timestamp'>) => {
    const newActivity: Activity = {
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      ...activityData,
    };

    setActivities(prev => [newActivity, ...prev.slice(0, 9)]); // Keep only last 10 activities
  };

  const clearActivities = () => {
    setActivities([]);
  };

  return (
    <ActivityContext.Provider value={{ activities, logActivity, clearActivities }}>
      {children}
    </ActivityContext.Provider>
  );
}

export function useActivity() {
  const context = useContext(ActivityContext);
  if (context === undefined) {
    throw new Error('useActivity must be used within an ActivityProvider');
  }
  return context;
}