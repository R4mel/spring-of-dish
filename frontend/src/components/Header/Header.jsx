import React from 'react';
import styles from './Header.module.css';

function Header() {
  return (
    <header className={styles.header}>
      {/* 왼쪽 아이콘 자리 (예: 햄버거 메뉴, 뒤로가기 등) */}
      <div className={styles.leftIcon}>
        {/* 아이콘 대신 텍스트나 SVG, FontAwesome, Material Icon 등을 넣을 수 있음 */}
        <span>≡</span>
      </div>

      {/* 중앙 타이틀 */}
      <h1 className={styles.title}>홈</h1>

      {/* 오른쪽 아이콘 자리 (예: 알림, 프로필, 추가 버튼 등) */}
      <div className={styles.rightIcon}>
        <span>＋</span>
      </div>
    </header>
  );
}

export default Header;
