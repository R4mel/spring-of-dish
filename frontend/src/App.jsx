import React from 'react';
import styles from './App.module.css';

// 컴포넌트 임포트
import Header from './components/Header/Header';
import MainContent from './components/MainContent/MainContent';
import BottomNav from './components/BottomNav/BottomNav';

function App() {
  return (
    <div className={styles.appContainer}>
      {/* 상단 헤더 */}
      <Header />

      {/* 메인 컨텐츠 */}
      <MainContent />

      {/* 하단 네비게이션 바 */}
      <BottomNav />
    </div>
  );
}

export default App;
