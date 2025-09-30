# SchedulePage Components

This directory contains the main schedule page components for the AI Time Management application.

## Components Overview

### MainSchedulePage.jsx
The main smart schedule page component that includes:
- **Task Management**: Hierarchical task list with categories and sub-tasks
- **Time Slots**: Interactive daily schedule with mood tracking
- **AI Recommendations**: Smart suggestions for task optimization
- **Statistics**: Visual charts and analytics
- **Real-time Status**: Live tracking of task completion

### SchedulePage.jsx
The success stories schedule page showing other users' achievements.

### Components Directory

#### TaskItem.jsx
Reusable component for displaying tasks with:
- Expandable sub-tasks
- Category badges (study, work, life, play)
- Status indicators (high-frequency, needs-improvement)
- Time tracking

#### TimeSlot.jsx
Interactive time slot component featuring:
- Mood tracking (happy, focused, tired)
- AI recommendation integration
- Task status management
- Notes and comments

#### StatCard.jsx
Simple statistics display card with customizable color themes.

#### TimeGrid.jsx & HeatMapLegend.jsx
Existing components for calendar and heatmap visualization.

## Features

### Smart Task Management
- **Categories**: Study (学习), Life (生活), Work (工作), Play (玩乐)
- **High-Frequency Tasks**: Marked with lightning bolt icon
- **Improvement Tasks**: Marked with warning icon for tasks to overcome
- **Search & Filter**: Real-time task filtering by category and keyword

### AI-Powered Recommendations
- **Time Optimization**: Suggests optimal time slots for different tasks
- **Efficiency Tips**: Provides task-specific improvement suggestions
- **Pattern Recognition**: Analyzes mood vs. task performance

### Mood & Performance Tracking
- **Mood Indicators**: Track emotional state during tasks
- **Performance Analytics**: Correlate mood with task completion rates
- **Behavioral Insights**: Identify optimal working conditions

### Visual Analytics
- **Weekly Progress Charts**: Bar charts showing time distribution
- **Category Breakdown**: Doughnut charts for task categorization
- **Completion Rates**: Progress tracking for different task types

## Usage

```jsx
import MainSchedulePage from './pages/SchedulePage/MainSchedulePage';

// Route setup
<Route path="/main-schedule" element={<MainSchedulePage />} />
```

## Dependencies

- **React 19.1.1**: Core framework
- **Chart.js 4.4.8**: Chart visualization
- **react-chartjs-2 5.2.0**: React wrapper for Chart.js
- **Font Awesome**: Icons
- **Tailwind CSS**: Styling

## Styling

The component uses:
- **MainSchedulePage.css**: Custom CSS variables and utilities
- **Tailwind CSS**: Utility-first styling
- **Custom Color Palette**: Theme-specific colors for different categories

## State Management

The component manages:
- `activeTab`: Current navigation tab
- `expandedTasks`: Which tasks are expanded to show sub-tasks
- `selectedMoods`: Mood selections for time slots
- `searchQuery`: Task search filter
- `showFullStats`: Statistics page visibility

## Data Structure

### Task Object
```javascript
{
  id: number,
  name: string,
  category: string,
  type: 'study' | 'life' | 'work' | 'play',
  isHighFrequency?: boolean,
  weeklyHours: number,
  subTasks?: Array<SubTask>
}
```

### Time Slot Object
```javascript
{
  id: number,
  time: string,
  task?: string,
  category?: string,
  type?: string,
  status: 'completed' | 'in-progress' | 'pending' | 'empty',
  note?: string,
  aiRecommendation?: string,
  mood?: 'happy' | 'focused' | 'tired'
}
```

## Customization

### Adding New Task Categories
1. Update the `getTaskColor()` function
2. Add new color variables in CSS
3. Update the filter buttons array

### Modifying AI Recommendations
1. Update the `timeSlots` data structure
2. Implement backend API integration
3. Add recommendation acceptance tracking

### Extending Analytics
1. Add new chart types in the statistics section
2. Implement data aggregation functions
3. Create new StatCard variants 