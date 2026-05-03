import 'package:flutter/material.dart';
import 'package:nutrition_app/theme/app_theme.dart';
import 'package:nutrition_app/screens/chat_screen.dart';
import 'home_screen.dart';
import 'log_food_screen.dart';
import 'history_screen.dart';
import 'profile_screen.dart';
import 'goals_screen.dart';

class MainTabs extends StatefulWidget {
  const MainTabs({super.key});

  @override
  State<MainTabs> createState() => _MainTabsState();
}

class _MainTabsState extends State<MainTabs> {
  int _index = 0;
  late List<Widget> _pages;

  final GlobalKey<HomeScreenState> _homeScreenKey = GlobalKey<HomeScreenState>();

  @override
  void initState() {
    super.initState();
    _pages = [
      HomeScreen(key: _homeScreenKey),
      const HistoryScreen(),
      const ChatScreen(),
      GoalsScreen(onGoalsUpdated: _refreshHomeScreen),
      const ProfileScreen(),
    ];
  }

  void _refreshHomeScreen() {
    _homeScreenKey.currentState?.refreshData();
  }

  void _navigateAndRefresh() {
    Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (context) => const LogFoodScreen(),
      ),
    ).then((result) {
      if (_index == 0) {
        _homeScreenKey.currentState?.refreshData();
      }
      ScaffoldMessenger.of(context)
        ..removeCurrentSnackBar()
        ..showSnackBar(const SnackBar(content: Text('Food Logged Successfully!')));
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _index,
        children: _pages,
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _navigateAndRefresh,
        backgroundColor: AppTheme.primary,
        foregroundColor: Colors.white,
        elevation: 8,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        child: const Icon(Icons.add, size: 28),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      bottomNavigationBar: BottomAppBar(
        shape: const CircularNotchedRectangle(),
        notchMargin: 10.0,
        color: AppTheme.surface,
        elevation: 0,
        padding: EdgeInsets.zero,
        clipBehavior: Clip.antiAlias,
        child: Container(
          decoration: BoxDecoration(
            border: Border(top: BorderSide(color: AppTheme.glassBorder, width: 1)),
          ),
          child: BottomNavigationBar(
            currentIndex: _index,
            onTap: (i) => setState(() => _index = i),
            type: BottomNavigationBarType.fixed,
            backgroundColor: AppTheme.surface,
            selectedItemColor: AppTheme.primary,
            unselectedItemColor: AppTheme.textSecondary,
            selectedFontSize: 12.0,
            unselectedFontSize: 10.0,
            elevation: 0,
            items: const [
              BottomNavigationBarItem(icon: Icon(Icons.home_outlined), activeIcon: Icon(Icons.home), label: 'Home'),
              BottomNavigationBarItem(icon: Icon(Icons.history_outlined), activeIcon: Icon(Icons.history), label: 'History'),
              // Placeholder for the FAB to center the other items
              BottomNavigationBarItem(icon: SizedBox.shrink(), label: ''),
              BottomNavigationBarItem(icon: Icon(Icons.flag_outlined), activeIcon: Icon(Icons.flag), label: 'Goals'),
              BottomNavigationBarItem(icon: Icon(Icons.person_outline), activeIcon: Icon(Icons.person), label: 'Profile'),
            ],
          ),
        ),
      ),
    );
  }
}
