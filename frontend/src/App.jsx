import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import styles from './App.module.css';

import HomePage from './pages/HomePage';
import IngredientPage from './pages/IngredientPage';
import FridgePage from './pages/FridgePage';  // ✨ 꼭 필요
import RecipePage from './pages/RecipePage';   // ✨ 있으면 가져오고

import Header from './components/Header/Header';
import BottomNav from './components/BottomNav/BottomNav';
import MainContent from './components/MainContent/MainContent'; // 홈 메인화면

function App() {
  return (
    <Router>
      <div className={styles.appContainer}>
        {/* 상단 헤더 */}
        <Header />

        {/* 메인 콘텐츠 */}
        <Routes>
          <Route path="/" element={<MainContent />} />            {/* 홈 메인 */}
          <Route path="/ingredient" element={<IngredientPage />} /> {/* 재료 추가 */}
          <Route path="/fridge" element={<FridgePage />} />         {/* 장바구니 페이지 */}
          <Route path="/recipe" element={<RecipePage />} />         {/* 레시피 페이지 */}
        </Routes>

        {/* 하단 네비게이션 */}
        <BottomNav />
      </div>
    </Router>
  );
}

export default App;
