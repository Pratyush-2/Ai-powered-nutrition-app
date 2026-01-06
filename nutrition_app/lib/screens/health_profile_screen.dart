import 'package:flutter/material.dart';
import 'package:nutrition_app/main.dart';
import 'package:nutrition_app/models/health_profile.dart';

class HealthProfileScreen extends StatefulWidget {
  const HealthProfileScreen({super.key});

  @override
  State<HealthProfileScreen> createState() => _HealthProfileScreenState();
}

class _HealthProfileScreenState extends State<HealthProfileScreen> {
  bool _isLoading = true;
  HealthProfile? _healthProfile;
  
  // Controllers for custom inputs
  final TextEditingController _allergyController = TextEditingController();
  final TextEditingController _intoleranceController = TextEditingController();
  
  @override
  void initState() {
    super.initState();
    _loadHealthProfile();
  }

  Future<void> _loadHealthProfile() async {
    try {
      final data = await apiService.getHealthProfile();
      setState(() {
        _healthProfile = HealthProfile.fromJson(data);
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading health profile: $e')),
        );
      }
    }
  }

  Future<void> _saveHealthProfile() async {
    if (_healthProfile == null) return;
    
    try {
      await apiService.updateHealthProfile(_healthProfile!.toJson());
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                SizedBox(width: 8),
                Text('Health profile saved!'),
              ],
            ),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error saving: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _addAllergy() {
    if (_allergyController.text.trim().isEmpty) return;
    
    setState(() {
      _healthProfile = _healthProfile!.copyWith(
        allergies: [..._healthProfile!.allergies, _allergyController.text.trim()],
      );
      _allergyController.clear();
    });
  }

  void _removeAllergy(String allergy) {
    setState(() {
      final allergies = List<String>.from(_healthProfile!.allergies);
      allergies.remove(allergy);
      _healthProfile = _healthProfile!.copyWith(allergies: allergies);
    });
  }

  void _addIntolerance() {
    if (_intoleranceController.text.trim().isEmpty) return;
    
    setState(() {
      _healthProfile = _healthProfile!.copyWith(
        intolerances: [..._healthProfile!.intolerances, _intoleranceController.text.trim()],
      );
      _intoleranceController.clear();
    });
  }

  void _removeIntolerance(String intolerance) {
    setState(() {
      final intolerances = List<String>.from(_healthProfile!.intolerances);
      intolerances.remove(intolerance);
      _healthProfile = _healthProfile!.copyWith(intolerances: intolerances);
    });
  }

  void _toggleDietaryRestriction(String restriction) {
    setState(() {
      final restrictions = List<String>.from(_healthProfile!.dietaryRestrictions);
      if (restrictions.contains(restriction)) {
        restrictions.remove(restriction);
      } else {
        restrictions.add(restriction);
      }
      _healthProfile = _healthProfile!.copyWith(dietaryRestrictions: restrictions);
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (_healthProfile == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Health Profile')),
        body: const Center(child: Text('Failed to load health profile')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Health Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.save),
            onPressed: _saveHealthProfile,
            tooltip: 'Save',
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Health Conditions Section
          _buildSectionHeader('🏥 Health Conditions', theme),
          const SizedBox(height: 12),
          _buildCheckboxTile(
            'Diabetes',
            _healthProfile!.hasDiabetes,
            (value) => setState(() {
              _healthProfile = _healthProfile!.copyWith(hasDiabetes: value);
            }),
          ),
          if (_healthProfile!.hasDiabetes)
            Padding(
              padding: const EdgeInsets.only(left: 32, top: 8),
              child: _buildDiabetesTypeSelector(),
            ),
          _buildCheckboxTile(
            'High Cholesterol',
            _healthProfile!.hasHighCholesterol,
            (value) => setState(() {
              _healthProfile = _healthProfile!.copyWith(hasHighCholesterol: value);
            }),
          ),
          _buildCheckboxTile(
            'Hypertension (High Blood Pressure)',
            _healthProfile!.hasHypertension,
            (value) => setState(() {
              _healthProfile = _healthProfile!.copyWith(hasHypertension: value);
            }),
          ),
          _buildCheckboxTile(
            'Heart Disease',
            _healthProfile!.hasHeartDisease,
            (value) => setState(() {
              _healthProfile = _healthProfile!.copyWith(hasHeartDisease: value);
            }),
          ),
          _buildCheckboxTile(
            'Kidney Disease',
            _healthProfile!.hasKidneyDisease,
            (value) => setState(() {
              _healthProfile = _healthProfile!.copyWith(hasKidneyDisease: value);
            }),
          ),
          _buildCheckboxTile(
            'Celiac Disease',
            _healthProfile!.hasCeliac,
            (value) => setState(() {
              _healthProfile = _healthProfile!.copyWith(hasCeliac: value);
            }),
          ),
          
          const SizedBox(height: 24),
          const Divider(),
          const SizedBox(height: 24),
          
          // Food Intolerances Section
          _buildSectionHeader('⚠️ Food Intolerances', theme),
          const SizedBox(height: 12),
          _buildCheckboxTile(
            'Lactose Intolerant',
            _healthProfile!.lactoseIntolerant,
            (value) => setState(() {
              _healthProfile = _healthProfile!.copyWith(lactoseIntolerant: value);
            }),
          ),
          _buildCheckboxTile(
            'Gluten Intolerant',
            _healthProfile!.glutenIntolerant,
            (value) => setState(() {
              _healthProfile = _healthProfile!.copyWith(glutenIntolerant: value);
            }),
          ),
          
          const SizedBox(height: 16),
          _buildCustomIntolerances(),
          
          const SizedBox(height: 24),
          const Divider(),
          const SizedBox(height: 24),
          
          // Food Allergies Section
          _buildSectionHeader('🚫 Food Allergies', theme),
          const SizedBox(height: 12),
          _buildCustomAllergies(),
          
          const SizedBox(height: 24),
          const Divider(),
          const SizedBox(height: 24),
          
          // Dietary Preferences Section
          _buildSectionHeader('🥗 Dietary Preferences', theme),
          const SizedBox(height: 12),
          _buildDietaryRestrictions(),
          
          const SizedBox(height: 32),
          
          // Save Button
          ElevatedButton.icon(
            onPressed: _saveHealthProfile,
            icon: const Icon(Icons.save),
            label: const Text('Save Health Profile'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.all(16),
              textStyle: const TextStyle(fontSize: 16),
            ),
          ),
          
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, ThemeData theme) {
    return Text(
      title,
      style: theme.textTheme.titleLarge?.copyWith(
        fontWeight: FontWeight.bold,
      ),
    );
  }

  Widget _buildCheckboxTile(String title, bool value, Function(bool) onChanged) {
    return CheckboxListTile(
      title: Text(title),
      value: value,
      onChanged: (newValue) => onChanged(newValue ?? false),
      contentPadding: EdgeInsets.zero,
    );
  }

  Widget _buildDiabetesTypeSelector() {
    return DropdownButtonFormField<String>(
      value: _healthProfile!.diabetesType,
      decoration: const InputDecoration(
        labelText: 'Diabetes Type',
        border: OutlineInputBorder(),
        contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      ),
      items: const [
        DropdownMenuItem(value: null, child: Text('Not specified')),
        DropdownMenuItem(value: 'type1', child: Text('Type 1')),
        DropdownMenuItem(value: 'type2', child: Text('Type 2')),
        DropdownMenuItem(value: 'gestational', child: Text('Gestational')),
      ],
      onChanged: (value) {
        setState(() {
          _healthProfile = _healthProfile!.copyWith(diabetesType: value);
        });
      },
    );
  }

  Widget _buildCustomAllergies() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _allergyController,
                decoration: const InputDecoration(
                  labelText: 'Add allergy',
                  hintText: 'e.g., Peanuts, Shellfish',
                  border: OutlineInputBorder(),
                ),
                onSubmitted: (_) => _addAllergy(),
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              icon: const Icon(Icons.add_circle),
              onPressed: _addAllergy,
              color: Theme.of(context).primaryColor,
            ),
          ],
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _healthProfile!.allergies.map((allergy) {
            return Chip(
              label: Text(allergy),
              deleteIcon: const Icon(Icons.close, size: 18),
              onDeleted: () => _removeAllergy(allergy),
              backgroundColor: Colors.red.shade50,
              deleteIconColor: Colors.red,
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildCustomIntolerances() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Custom Intolerances:', style: TextStyle(fontWeight: FontWeight.w500)),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _intoleranceController,
                decoration: const InputDecoration(
                  labelText: 'Add intolerance',
                  hintText: 'e.g., Soy, Nightshades',
                  border: OutlineInputBorder(),
                ),
                onSubmitted: (_) => _addIntolerance(),
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              icon: const Icon(Icons.add_circle),
              onPressed: _addIntolerance,
              color: Theme.of(context).primaryColor,
            ),
          ],
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: _healthProfile!.intolerances.map((intolerance) {
            return Chip(
              label: Text(intolerance),
              deleteIcon: const Icon(Icons.close, size: 18),
              onDeleted: () => _removeIntolerance(intolerance),
              backgroundColor: Colors.orange.shade50,
              deleteIconColor: Colors.orange,
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildDietaryRestrictions() {
    final restrictions = ['Vegetarian', 'Vegan', 'Halal', 'Kosher'];
    
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: restrictions.map((restriction) {
        final isSelected = _healthProfile!.dietaryRestrictions
            .contains(restriction.toLowerCase());
        
        return FilterChip(
          label: Text(restriction),
          selected: isSelected,
          onSelected: (_) => _toggleDietaryRestriction(restriction.toLowerCase()),
          selectedColor: Theme.of(context).primaryColor.withOpacity(0.2),
          checkmarkColor: Theme.of(context).primaryColor,
        );
      }).toList(),
    );
  }

  @override
  void dispose() {
    _allergyController.dispose();
    _intoleranceController.dispose();
    super.dispose();
  }
}
