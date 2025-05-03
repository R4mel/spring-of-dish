import React, { useState, useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import styles from "./FridgePage.module.css";
import INGREDIENTS_DATA from "../data/IngredientData";

export default function FridgePage() {
  // 1. 선택 모드 상태
  const [isSelecting, setIsSelecting] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);

  // 2. 재료 리스트 상태
  const location = useLocation();
  const [ingredients, setIngredients] = useState(
    location.state?.selectedIngredients || []
  );

  // 3. 모달 및 날짜 상태
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedIngredient, setSelectedIngredient] = useState(null);
  const [storedDate, setStoredDate] = useState("");
  const [expireDate, setExpireDate] = useState("");
  const [isFrozen, setIsFrozen] = useState(false);

  // 4. 추천 소비기한 일수 맵
  const RECOMMEND_DAYS = {
    // (기존 RECOMMEND_DAYS 그대로 복사)
    계란: 35,
    메추리알: 35,
    감자: 4,
    고구마: 4,
    누룽지: 45,
    밀가루: 45,
    빵가루: 45,
    쌀: 45,
    옥수수콘: 45,
    오트밀: 45,
    찹쌀가루: 45,
    감: 7,
    건포도: 180,
    귤: 10,
    딸기: 5,
    라임: 14,
    레몬: 14,
    망고: 10,
    멜론: 7,
    바나나: 5,
    배: 14,
    복숭아: 5,
    블루베리: 7,
    사과: 30,
    수박: 7,
    아보카도: 7,
    오렌지: 14,
    자두: 5,
    자몽: 14,
    체리: 5,
    키위: 14,
    파인애플: 7,
    포도: 7,
    가지: 7,
    고추: 7,
    깻잎: 7,
    당근: 14,
    대파: 10,
    마늘: 30,
    무: 14,
    열무: 5,
    바질: 3,
    배추: 14,
    브로콜리: 7,
    비트: 14,
    시금치: 5,
    아스파라거스: 5,
    상추: 5,
    샐러리: 7,
    애호박: 7,
    양배추: 14,
    양송이버섯: 7,
    팽이버섯: 7,
    표고버섯: 7,
    양파: 30,
    오이: 7,
    콩나물: 5,
    토마토: 5,
    파프리카: 7,
    호박: 7,
    가래떡: 7,
    떡국떡: 7,
    바게트: 3,
    베이글: 5,
    식빵: 5,
    버터: 30,
    생크림: 7,
    요거트: 14,
    우유: 7,
    치즈: 14,
    닭고기: 3,
    돼지고기: 3,
    소고기: 3,
    양고기: 3,
    오리고기: 3,
    검은콩: 180,
    땅콩: 180,
    병아리: 180,
    아몬드: 180,
    완두: 180,
    팥: 180,
    피스타치오: 180,
    호두: 180,
    낙지젓: 30,
    명란젓: 30,
    새우젓: 30,
    오징어젓: 30,
    김치: 14,
    두부: 7,
    베이컨: 7,
    소세지: 7,
    어묵: 7,
    유부: 7,
    진미채: 30,
    참치캔: 365,
    스팸: 365,
    갈치: 3,
    고등어: 3,
    꽁치: 3,
    건새우: 180,
    게맛살: 7,
    굴: 3,
    골뱅이: 7,
    꽃게: 3,
    꼬막: 3,
    낙지: 3,
    동태: 3,
    대합: 3,
    다시마: 365,
    도다리: 3,
    명태: 3,
    멸치: 180,
    미역: 365,
    문어: 3,
    바지락: 3,
    새우: 3,
    소라: 7,
    아귀: 3,
    연어: 3,
    오징어: 3,
    조기: 3,
    전어: 3,
    조개: 3,
    쭈꾸미: 3,
    전복: 7,
    홍합: 7,
  };

  const navigate = useNavigate();

  // 5. 선택된 재료 카테고리 조회
  const selectedCategory = useMemo(() => {
    if (!selectedIngredient) return "";
    for (const [cat, items] of Object.entries(INGREDIENTS_DATA)) {
      if (items.some((i) => i.name === selectedIngredient.name)) {
        return cat;
      }
    }
    return "";
  }, [selectedIngredient]);

  // 6. 재료 그룹핑
  const grouped = useMemo(() => {
    return ingredients.reduce((acc, ing) => {
      const found = Object.entries(INGREDIENTS_DATA).find(([cat, items]) =>
        items.some((item) => item.name === ing.name)
      );
      const category = found ? found[0] : "기타";
      if (!acc[category]) acc[category] = [];
      acc[category].push(ing);
      return acc;
    }, {});
  }, [ingredients]);

  // -- 핸들러: 선택 모드 토글
  const toggleSelecting = () => {
    setIsSelecting((prev) => {
      if (prev) setSelectedItems([]);
      return !prev;
    });
  };

  // -- 핸들러: 재료 클릭
  const handleIngredientClick = (ingredient) => {
    if (isSelecting) {
      const already = selectedItems.some((i) => i.name === ingredient.name);
      setSelectedItems((prev) =>
        already
          ? prev.filter((i) => i.name !== ingredient.name)
          : [...prev, ingredient]
      );
    } else {
      setSelectedIngredient(ingredient);
      setIsFrozen(false);

      // 오늘 날짜 설정
      const today = new Date();
      const fmt = (n) => String(n).padStart(2, "0");
      const todayStr = `${today.getFullYear()}-${fmt(
        today.getMonth() + 1
      )}-${fmt(today.getDate())}`;
      setStoredDate(todayStr);

      // 기본 소비기한 계산
      const daysToAdd = RECOMMEND_DAYS[ingredient.name] ?? 30;
      const exp = new Date(today);
      exp.setDate(exp.getDate() + daysToAdd);
      const expireStr = `${exp.getFullYear()}-${fmt(exp.getMonth() + 1)}-${fmt(
        exp.getDate()
      )}`;
      setExpireDate(expireStr);

      setIsModalOpen(true);
    }
  };

  // -- 핸들러: 저장된 날짜 변경
  const handleStoredDateChange = (e) => {
    const raw = e.target.value;
    const parts = raw.match(/\d+/g);
    if (!parts || parts.length < 3) return;
    const [y, m, d] = parts.map((v) => parseInt(v, 10));
    const newStored = `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(
      2,
      "0"
    )}`;
    setStoredDate(newStored);

    const daysToAdd = RECOMMEND_DAYS[selectedIngredient.name] ?? 30;
    const base = new Date(y, m - 1, d);
    base.setDate(base.getDate() + daysToAdd);
    const fmt = (n) => String(n).padStart(2, "0");
    const newExpire = `${base.getFullYear()}-${fmt(base.getMonth() + 1)}-${fmt(
      base.getDate()
    )}`;
    setExpireDate(newExpire);
  };

  // -- 핸들러: 소비기한 변경
  const handleExpireDateChange = (e) => {
    setExpireDate(e.target.value);
  };

  // -- 핸들러: 냉동 토글
  const handleFreezeToggle = () => {
    const nextFrozen = !isFrozen;
    setIsFrozen(nextFrozen);

    if (nextFrozen) {
      const [y, m, d] = storedDate.split("-").map(Number);
      const dt = new Date(y, m - 1, d);
      dt.setMonth(dt.getMonth() + 3);
      const fmt = (n) => String(n).padStart(2, "0");
      setExpireDate(
        `${dt.getFullYear()}-${fmt(dt.getMonth() + 1)}-${fmt(dt.getDate())}`
      );
    } else {
      if (selectedIngredient) {
        const daysToAdd = RECOMMEND_DAYS[selectedIngredient.name] ?? 30;
        const [y, m, d] = storedDate.split("-").map(Number);
        const dt2 = new Date(y, m - 1, d);
        dt2.setDate(dt2.getDate() + daysToAdd);
        const fmt2 = (n) => String(n).padStart(2, "0");
        setExpireDate(
          `${dt2.getFullYear()}-${fmt2(dt2.getMonth() + 1)}-${fmt2(
            dt2.getDate()
          )}`
        );
      }
    }
  };

  // -- 핸들러: 모달 닫기
  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedIngredient(null);
  };

  // -- 핸들러: 날짜 저장
  const handleSaveDate = () => {
    if (!selectedIngredient) return;
    const updated = ingredients.map((item) =>
      item.name === selectedIngredient.name ? { ...item, expireDate } : item
    );
    setIngredients(updated);
    closeModal();
  };

  // -- 핸들러: 삭제
  const handleDeleteItem = () => {
    const filtered = ingredients.filter(
      (item) => item.name !== selectedIngredient.name
    );
    setIngredients(filtered);
    closeModal();
  };

  // 날짜 표시 헬퍼
  const formatDisplayDate = (dateStr) => {
    const [year, month, day] = dateStr.split("-");
    return `${year.slice(2)}/${month}/${day}`;
  };

  return (
    <div className={styles.pageContainer}>
      {/* 선택 모드 버튼 */}
      <button className={styles.selectButton} onClick={toggleSelecting}>
        선택
      </button>

      {/* 선택 개수 표시 */}
      {isSelecting && (
        <div className={styles.selectedCount}>
          {selectedItems.length}개 선택됨
        </div>
      )}

      <h2 className={styles.pageTitle}>곰이네 냉장고ʕ•ᴥ•ʔ</h2>

      {/* 재료 목록 */}
      {Object.entries(grouped).map(([category, items]) => (
        <section key={category}>
          <h3 className={styles.categoryTitle}>{category}</h3>
          <div className={styles.ingredientsList}>
            {items.map((ingredient) => {
              const isSelected = selectedItems.some(
                (i) => i.name === ingredient.name
              );
              return (
                <div
                  key={ingredient.name}
                  className={`${styles.ingredientItem} ${
                    isSelecting && isSelected ? styles.selectedItem : ""
                  }`}
                  onClick={() => handleIngredientClick(ingredient)}
                >
                  <img
                    src={ingredient.icon}
                    alt={ingredient.name}
                    className={styles.ingredientIcon}
                  />
                  <p className={styles.ingredientName}>
                    {ingredient.name}
                    {ingredient.expireDate && (
                      <span className={styles.expireDate}>
                        ({formatDisplayDate(ingredient.expireDate)})
                      </span>
                    )}
                  </p>
                </div>
              );
            })}
          </div>
        </section>
      ))}

      {/* 모달 */}
      {isModalOpen && selectedIngredient && (
        <div className={styles.modalBackdrop}>
          <div className={styles.modalContent}>
            <img
              src={selectedIngredient.icon}
              alt={selectedIngredient.name}
              className={styles.modalImage}
            />
            <h2 className={styles.modalTitle}>{selectedIngredient.name}</h2>
            <p className={styles.modalSubtitle}>
              {selectedCategory}{" "}
              {isFrozen && <span style={{ color: "skyblue" }}>냉동 보관</span>}
            </p>

            <div className={styles.dateSection}>
              <div className={styles.dateItem}>
                <span>추가된 날짜</span>
                <input
                  type="date"
                  value={storedDate}
                  onChange={handleStoredDateChange}
                />
              </div>
              <div className={styles.dateItem}>
                <span>소비기한 마감</span>
                <input
                  type="date"
                  value={expireDate}
                  onChange={handleExpireDateChange}
                />
              </div>
            </div>

            <div className={styles.buttonSection}>
              <button
                className={styles.freezeButton}
                onClick={handleFreezeToggle}
              >
                ❄️ 냉동
              </button>
              <button
                className={styles.deleteButton}
                onClick={handleDeleteItem}
              >
                🗑️ 삭제
              </button>
            </div>

            <div className={styles.modalButtons}>
              <button onClick={handleSaveDate}>저장</button>
              <button onClick={closeModal}>닫기</button>
            </div>
          </div>
        </div>
      )}

      {/* 요리시작 버튼 */}
      <button
        className={styles.startButton}
        onClick={() => navigate("/recipe")}
      >
        요리시작
      </button>
    </div>
  );
}
