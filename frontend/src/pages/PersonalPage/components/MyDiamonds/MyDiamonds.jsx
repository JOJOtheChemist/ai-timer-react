import React from 'react';
import './MyDiamonds.css';

const MyDiamonds = ({ assets, onRecharge }) => {
  return (
    <div className="asset-section">
      <div>
        <div className="asset-info">
          <div className="asset-icon">💎</div>
          <div className="asset-detail">
            <div className="asset-title">我的钻石</div>
            <div className="asset-value">{assets?.diamond_count || 0}</div>
            <div className="consume-record">
              {assets?.recent_consume ? 
                `最近：${assets.recent_consume.description} ${Math.abs(assets.recent_consume.amount)}钻石` :
                '暂无消费记录'
              }
            </div>
          </div>
        </div>
      </div>
      <button className="recharge-btn" onClick={onRecharge}>充值</button>
    </div>
  );
};

export default MyDiamonds; 