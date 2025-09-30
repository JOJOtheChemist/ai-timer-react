import React from 'react';
import UserTopNav from '../../components/Navbar/UserTopNav';
import BottomNavBar from '../../components/Navbar/BottomNavBar';
import './StudyMethodPage.css';

const StudyMethodPage = () => {
  return (
    <div className="study-method-page bg-gray-50 font-sans text-gray-800">
      <UserTopNav />
                            
      <main className="px-4 py-3 pb-24">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h1 className="text-2xl font-bold text-center mb-4">学习方法区</h1>
          <p className="text-gray-600 text-center">
            这里将展示各种学习方法和技巧，帮助你提高学习效率。
          </p>
          <div className="mt-8 text-center">
            <div className="inline-flex items-center justify-center w-24 h-24 bg-blue-100 rounded-full mb-4">
              <i className="fa fa-book text-3xl text-blue-600"></i>
            </div>
            <p className="text-gray-500">功能开发中，敬请期待...</p>
            </div>
        </div>
    </main>

      <BottomNavBar />
    </div>
  );
};

export default StudyMethodPage;
