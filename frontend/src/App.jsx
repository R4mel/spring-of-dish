// import React from "react";
// import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import styles from "./App.module.css";

// import HomePage from "./pages/HomePage";
// import RedirectPage from "./pages/RedirectPage";
// import ProfilePage from "./pages/ProfilePage";
// import MessagePage from "./pages/MessagePage";

// import IngredientPage from "./pages/IngredientPage";
// import FridgePage from "./pages/FridgePage";
// import RecipePage from "./pages/RecipePage";
// import LogoutPage from "./pages/LogoutPage";
// import Header from "./components/Header/Header";
// import BottomNav from "./components/BottomNav/BottomNav";
// import MainContent from "./components/MainContent/MainContent";
// import LoginPage from './pages/LoginPage';
// import OAuthCallback from './pages/OAuthCallback';

// export default function App() {
//   return (
//     <Router>
//       <div className={styles.appContainer}>
//         {/* 상단 헤더 */}
//         <Header />

//         {/* 메인 콘텐츠 */}
//         <Routes>
//           <Route path="/" element={<MainContent />} /> {/* 홈 메인 */}
//           <Route path="/redirect" element={<RedirectPage />} />{" "}
//           {/* OAuth 콜백 */}
//           <Route path="/profile" element={<ProfilePage />} /> {/* 내 프로필 */}
//           <Route path="/message" element={<MessagePage />} /> {/* 내 메시지 */}
//           <Route path="/ingredient" element={<IngredientPage />} />{" "}
//           {/* 재료 추가 */}
//           <Route path="/fridge" element={<FridgePage />} />{" "}
//           {/* 냉장고 페이지 */}
//           <Route path="/recipe" element={<RecipePage />} />{" "}
//           {/* 레시피 페이지 */}
//           <Route path="/login" element={<LoginPage />} />
//           <Route path="/auth/callback" element={<OAuthCallback />} />
//           <Route path="/" element={<MainContent />} />
//         </Routes>

//         {/* 하단 네비게이션 */}
//         <BottomNav />
//       </div>
//     </Router>
//   );
// }
// import React from "react";
// import {
//   BrowserRouter as Router,
//   Routes,
//   Route,
//   Navigate,            // ← import this
// } from "react-router-dom";
// import styles from "./App.module.css";

// import MainContent from "./components/MainContent/MainContent";
// import Header from "./components/Header/Header";
// import BottomNav from "./components/BottomNav/BottomNav";

// import HomePage from "./pages/HomePage";
// import RedirectPage from "./pages/RedirectPage";
// import ProfilePage from "./pages/ProfilePage";
// import MessagePage from "./pages/MessagePage";
// import IngredientPage from "./pages/IngredientPage";
// import FridgePage from "./pages/FridgePage";
// import RecipePage from "./pages/RecipePage";
// import LogoutPage from "./pages/LogoutPage";
// import LoginPage from "./pages/LoginPage";           // ← your login page
// import OAuthCallback from "./pages/OAuthCallback";

// export default function App() {
//   return (
//     <Router>
//       <div className={styles.appContainer}>w  ``
//         <Header />

//         <Routes>
//           {/* 1) Redirect the root path "/" to "/login" */}
//           <Route path="/" element={<Navigate to="/login" replace />} />

//           {/* 2) Your actual routes */}
//           <Route path="/login" element={<LoginPage />} />
//           <Route path="/auth/callback" element={<OAuthCallback />} />
//           <Route path="/redirect" element={<RedirectPage />} />

//           {/* Once logged in, you can show MainContent on a different path */}
//           <Route path="/home" element={<MainContent />} />

//           <Route path="/profile" element={<ProfilePage />} />
//           <Route path="/message" element={<MessagePage />} />
//           <Route path="/ingredient" element={<IngredientPage />} />
//           <Route path="/fridge" element={<FridgePage />} />
//           <Route path="/recipe" element={<RecipePage />} />
//           <Route path="/logout" element={<LogoutPage />} />

//           {/* (Optional) Catch-all: if user manually types unknown URL, redirect to login */}
//           <Route path="*" element={<Navigate to="/login" replace />} />
//         </Routes>

//         <BottomNav />
//       </div>
//     </Router>
//   );
// }

import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import styles from "./App.module.css";

import Header from "./components/Header/Header";
import BottomNav from "./components/BottomNav/BottomNav";

import LoginPage from "./pages/LoginPage";
import OAuthCallback from "./pages/OAuthCallback";
import RedirectPage from "./pages/RedirectPage";

import MainContent from "./components/MainContent/MainContent";
import ProfilePage from "./pages/ProfilePage";
import MessagePage from "./pages/MessagePage";
import IngredientPage from "./pages/IngredientPage";
import FridgePage from "./pages/FridgePage";
import RecipePage from "./pages/RecipePage";
import LogoutPage from "./pages/LogoutPage";

export default function App() {
  return (
    <Router>
      <div className={styles.appContainer}>
        <Header />

        <Routes>
          {/* 1) Root → Login */}
          <Route path="/" element={<Navigate to="/login" replace />} />

          {/* 2) Auth routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<OAuthCallback />} />
          <Route path="/redirect" element={<RedirectPage />} />

          {/* 3) Post-login */}
          <Route path="/home" element={<MainContent />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/message" element={<MessagePage />} />
          <Route path="/ingredient" element={<IngredientPage />} />
          <Route path="/fridge" element={<FridgePage />} />
          <Route path="/recipe" element={<RecipePage />} />
          <Route path="/logout" element={<LogoutPage />} />

          {/* 4) Fallback */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>

        <BottomNav />
      </div>
    </Router>
  );
}