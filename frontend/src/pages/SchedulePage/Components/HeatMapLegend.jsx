import React from 'react';

const HeatMapLegend = ({ heatmapData }) => {
  return (
    <div className="heatmap-legend">
      <div className="legend-title">
        <h4>学习强度</h4>
      </div>
      
      <div className="legend-content">
        <div className="intensity-scale">
          <span className="scale-label">少</span>
          <div className="scale-boxes">
            <div className="scale-box intensity-0"></div>
            <div className="scale-box intensity-1"></div>
            <div className="scale-box intensity-2"></div>
            <div className="scale-box intensity-3"></div>
            <div className="scale-box intensity-4"></div>
          </div>
          <span className="scale-label">多</span>
        </div>
        
        <div className="heatmap-stats">
          <p>数据点: {heatmapData.length}</p>
          <p>最高强度: {Math.max(...heatmapData.map(d => d.intensity || 0), 0)}</p>
          <p>平均强度: {
            heatmapData.length > 0 
              ? (heatmapData.reduce((sum, d) => sum + (d.intensity || 0), 0) / heatmapData.length).toFixed(1)
              : 0
          }</p>
        </div>
      </div>
      
      <style jsx>{`
        .intensity-scale {
          display: flex;
          align-items: center;
          gap: 8px;
          margin: 12px 0;
        }
        
        .scale-boxes {
          display: flex;
          gap: 2px;
        }
        
        .scale-box {
          width: 12px;
          height: 12px;
          border-radius: 2px;
          border: 1px solid #e1e5e9;
        }
        
        .intensity-0 { background-color: #ebedf0; }
        .intensity-1 { background-color: #c6e48b; }
        .intensity-2 { background-color: #7bc96f; }
        .intensity-3 { background-color: #239a3b; }
        .intensity-4 { background-color: #196127; }
        
        .scale-label {
          font-size: 12px;
          color: #586069;
        }
        
        .heatmap-stats p {
          margin: 4px 0;
          font-size: 14px;
          color: #586069;
        }
      `}</style>
    </div>
  );
};

export default HeatMapLegend; 