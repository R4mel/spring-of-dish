import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import styles from "./App.module.css";

import HomePage from "./pages/HomePage";
import RedirectPage from "./pages/RedirectPage";
import ProfilePage from "./pages/ProfilePage";
import MessagePage from "./pages/MessagePage";

import IngredientPage from "./pages/IngredientPage";
import FridgePage from "./pages/FridgePage";
import RecipePage from "./pages/RecipePage";
import LogoutPage from "./pages/LogoutPage";
import Header from "./components/Header/Header";
import BottomNav from "./components/BottomNav/BottomNav";
import MainContent from "./components/MainContent/MainContent";
import LoginPage from './pages/LoginPage';
import OAuthCallback from './pages/OAuthCallback';

export default function App() {
  return (
    <Router>
      <div className={styles.appContainer}>
        {/* 상단 헤더 */}
        <Header />

        {/* 메인 콘텐츠 */}
        <Routes>
          <Route path="/" element={<MainContent />} /> {/* 홈 메인 */}
          <Route path="/redirect" element={<RedirectPage />} />{" "}
          {/* OAuth 콜백 */}
          <Route path="/profile" element={<ProfilePage />} /> {/* 내 프로필 */}
          <Route path="/message" element={<MessagePage />} /> {/* 내 메시지 */}
          <Route path="/ingredient" element={<IngredientPage />} />{" "}
          {/* 재료 추가 */}
          <Route path="/fridge" element={<FridgePage />} />{" "}
          {/* 냉장고 페이지 */}
          <Route path="/recipe" element={<RecipePage />} />{" "}
          {/* 레시피 페이지 */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<OAuthCallback />} />
          <Route path="/" element={<MainContent />} />
        </Routes>

        {/* 하단 네비게이션 */}
        <BottomNav />
      </div>
    </Router>
  );
}
