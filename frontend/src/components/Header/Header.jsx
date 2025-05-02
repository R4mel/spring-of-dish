// Header.jsx
import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import styles from './Header.module.css';

function Header() {
  const location = useLocation();
  const navigate = useNavigate();

  const pathname = location.pathname;

  if (pathname === '/') {
    // 1) 메인 페이지
    return (
      <header className={styles.header}>
        <h2 className={styles.centerTitle}>홈</h2>
        <button
          className={styles.rightButton}
          onClick={() => navigate('/ingredient')}
        >
          <img src="/assets/plus.png" alt="plus" />
        </button>
      </header>
    );
  } else if (pathname === '/ingredient') {
    // 2) 재료 추가 페이지
    return (
      <header className={styles.header}>
        <button
          className={styles.leftButton}
          onClick={() => navigate('/')}
        >
          {/* 뒤로가기 아이콘 이미지 (파일 경로는 상황에 맞게 조정) */}
          <img
            src="/assets/reply.png"
            alt="뒤로가기"
            className={styles.backIcon}
          />
        </button>
        <h2 className={styles.centerTitle}>재료 추가</h2>
        {/* 오른쪽 영역 자리 채우기용 빈 요소 (타이틀 중앙 정렬 유지) */}
        <div className={styles.rightPlaceholder}></div>
      </header>
    );
  } else if (pathname === '/fridge') {
    // 3) 냉장고 페이지
    return (
      <header className={styles.header}>
        <button
          className={styles.leftButton}
          onClick={() => navigate('/ingredient')}
        >
          <img
            src="/assets/reply.png"
            alt="뒤로가기"
            className={styles.backIcon}
          />
        </button>
        <h2 className={styles.centerTitle}>냉장고 앱</h2>
        <div className={styles.rightPlaceholder}></div>
      </header>
    );
  } else if (pathname === '/recipe') {
    // 4 ) 요리 보기 페이지
    return (
      <header className={styles.header}>
        {/* 왼쪽 뒤로가기 버튼 */}
        <button
          className={styles.leftButton}
          onClick={() => navigate('/fridge')}
        >
          {/* 뒤로가기 아이콘 이미지 (파일 경로는 상황에 맞게 조정) */}
          <img
            src="/assets/reply.png"
            alt="뒤로가기"
            className={styles.backIcon}
          />
        </button>
        <h2 className={styles.centerTitle}>요리 보기</h2>
        {/* 오른쪽 + 아이콘 */}
        <button
          className={styles.rightButton}
          onClick={() => navigate('/ingredient')}
        >
          <img src="/assets/plus.png" alt="plus" />
        </button>
      </header>
    );
  } else {
    // 그 외 경로 (예: 404나 다른 페이지)
    return (
      <header className={styles.header}>
        <h2 className={styles.centerTitle}>냉장고 앱</h2>
      </header>
    );
  }
}

export default Header;
