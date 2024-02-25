import styles from './component/searchbar.module.css';
export default function RootLayout({
    children,
  }: Readonly<{
    children: React.ReactNode;
  }>){
    return (
      <div className={styles.rootLayout}>
      {children}
    </div>
    );
  }