import 'package:flutter/material.dart';
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
        child: const Icon(Icons.add),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      bottomNavigationBar: BottomAppBar(
        shape: const CircularNotchedRectangle(),
        notchMargin: 8.0,
        child: BottomNavigationBar(
          currentIndex: _index,
          onTap: (i) => setState(() => _index = i),
          type: BottomNavigationBarType.fixed,
          selectedFontSize: 12.0,
          unselectedFontSize: 10.0,
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
            BottomNavigationBarItem(icon: Icon(Icons.history), label: 'History'),
            // Placeholder for the FAB to center the other items
            BottomNavigationBarItem(icon: Icon(Icons.chat_bubble_outline), label: 'Chat'),
            BottomNavigationBarItem(icon: Icon(Icons.flag), label: 'Goals'),
            BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
          ],
        ),
      ),
    );
  }
}
