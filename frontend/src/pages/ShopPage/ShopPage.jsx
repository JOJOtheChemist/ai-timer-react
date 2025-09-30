import React from 'react';
import UserTopNav from '../../components/Navbar/UserTopNav';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './ShopPage.css';

const ShopPage = () => {
  return (
    <div className="shop-page bg-gray-50 font-sans text-gray-800">
      <UserTopNav />
      
      <main className="px-4 py-3 pb-24">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h1 className="text-xl font-semibold mb-4">商城</h1>
          <p className="text-gray-600">这里是商城页面内容...</p>
        </div>
      </main>

      <BottomNavBar />
    </div>
  );
};

export default ShopPage;
