import React from "react";
import styles from "./BottomNav.module.css";

function BottomNav() {
  return (
    <nav className={styles.bottomNav}>
      <div className={styles.navItem}>
        <span>홈</span>
      </div>
      <div className={styles.navItem}>
        <span>레시피</span>
      </div>
      <div className={styles.navItem}>
        <span>냉장고</span>
      </div>
    </nav>
  );
}

export default BottomNav;
