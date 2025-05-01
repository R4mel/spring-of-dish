import React from 'react';
import styles from './BottomNav.module.css';

function BottomNav() {
  return (
    <nav className={styles.bottomNav}>
      <div className={styles.navItem}>
        <a href="/">홈</a>
      </div>
      <div className={styles.navItem}>
        <a href="/recipe">레시피</a>
      </div>
      <div className={styles.navItem}>
        <a href="/fridge">냉장고</a>
      </div>
    </nav>
  );
}

export default BottomNav;