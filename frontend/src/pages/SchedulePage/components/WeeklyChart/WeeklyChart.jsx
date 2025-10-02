import React from 'react';
import { Bar } from 'react-chartjs-2';
import './WeeklyChart.css';

const WeeklyChart = ({ chartData, chartOptions }) => {
  return (
    <div className="weekly-chart-container">
      <h3 className="chart-title">本周时间分布</h3>
      <div className="chart-wrapper">
        <Bar data={chartData} options={chartOptions} />
      </div>
    </div>
  );
};

export default WeeklyChart; 