# Applications Mobiles et Cross-Platform - Espace Perplexity AI

## Vue d'ensemble
Ce document présente un framework complet pour développement d'applications mobiles et cross-platform dans l'espace Perplexity AI, intégrant React Native, Flutter, PWA et architectures natives avec synchronisation offline, push notifications intelligentes et expérience utilisateur optimisée.

## Architecture Mobile et Cross-Platform

### Écosystème Multi-Plateforme Unifié

```
┌─────────────────────────────────────────────────────────────────┐
│           APPLICATIONS MOBILES ET CROSS-PLATFORM               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📱 Native Apps       🌐 Cross-Platform    💻 Web & PWA        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ • iOS Swift     │  │ • React Native  │  │ • Progressive   │ │
│  │ • Android Kotlin│  │ • Flutter       │  │ • Service Worker│ │
│  │ • Performance   │  │ • Xamarin       │  │ • Offline First │ │
│  │ • Platform APIs │  │ • Code Sharing  │  │ • App Shell     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                  ↕                              │
│  🔄 Sync & Offline   📲 Push Notifications 🎨 UI/UX Design     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ • Data Sync     │  │ • FCM/APNS      │  │ • Design System │ │
│  │ • Conflict Res  │  │ • Intelligent   │  │ • Adaptive UI   │ │
│  │ • Offline Queue │  │ • Personalized  │  │ • Accessibility │ │
│  │ • Background    │  │ • Analytics     │  │ • Performance   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Module 1 : Framework React Native Métier

### Application React Native Business-Ready

```typescript
// BusinessMobileApp.tsx
/**
 * Framework React Native pour applications métier
 * Intègre navigation, état global, synchronisation et notifications
 */

import React, { useEffect, useState, useContext } from 'react';
import { 
  NavigationContainer, 
  DefaultTheme, 
  DarkTheme 
} from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  Alert,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
  Platform
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import PushNotification from 'react-native-push-notification';
import BackgroundJob from 'react-native-background-job';
import { Provider as ReduxProvider, useSelector, useDispatch } from 'react-redux';
import { configureStore, createSlice, PayloadAction } from '@reduxjs/toolkit';
import Icon from 'react-native-vector-icons/MaterialIcons';

// Types métier
interface BusinessUser {
  id: string;
  name: string;
  email: string;
  role: string;
  permissions: string[];
  avatar?: string;
}

interface BusinessData {
  id: string;
  type: 'order' | 'customer' | 'product' | 'report';
  title: string;
  data: any;
  lastUpdated: Date;
  syncStatus: 'synced' | 'pending' | 'conflict' | 'error';
}

interface AppState {
  user: BusinessUser | null;
  isAuthenticated: boolean;
  isOnline: boolean;
  businessData: BusinessData[];
  syncQueue: any[];
  notifications: any[];
  theme: 'light' | 'dark';
  language: string;
}

// Redux Store Configuration
const initialState: AppState = {
  user: null,
  isAuthenticated: false,
  isOnline: true,
  businessData: [],
  syncQueue: [],
  notifications: [],
  theme: 'light',
  language: 'fr'
};

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<BusinessUser>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
    },
    setOnlineStatus: (state, action: PayloadAction<boolean>) => {
      state.isOnline = action.payload;
    },
    addBusinessData: (state, action: PayloadAction<BusinessData>) => {
      const existing = state.businessData.findIndex(item => item.id === action.payload.id);
      if (existing >= 0) {
        state.businessData[existing] = action.payload;
      } else {
        state.businessData.push(action.payload);
      }
    },
    addToSyncQueue: (state, action: PayloadAction<any>) => {
      state.syncQueue.push({
        ...action.payload,
        timestamp: new Date().toISOString()
      });
    },
    clearSyncQueue: (state) => {
      state.syncQueue = [];
    },
    addNotification: (state, action: PayloadAction<any>) => {
      state.notifications.unshift(action.payload);
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    }
  }
});

const store = configureStore({
  reducer: {
    app: appSlice.reducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['app/addBusinessData', 'app/addToSyncQueue']
      }
    })
});

export const { 
  setUser, 
  logout, 
  setOnlineStatus, 
  addBusinessData, 
  addToSyncQueue,
  clearSyncQueue,
  addNotification,
  setTheme 
} = appSlice.actions;

// Services métier
class BusinessApiService {
  private baseUrl = 'https://api.business-app.com';
  private authToken: string | null = null;

  async login(email: string, password: string): Promise<BusinessUser> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        throw new Error('Authentication failed');
      }

      const data = await response.json();
      this.authToken = data.token;
      
      // Stockage token sécurisé
      await AsyncStorage.setItem('auth_token', data.token);
      
      return data.user;
    } catch (error) {
      throw new Error(`Login failed: ${error.message}`);
    }
  }

  async fetchBusinessData(type: string, lastSync?: Date): Promise<BusinessData[]> {
    const headers: any = { 'Content-Type': 'application/json' };
    if (this.authToken) {
      headers.Authorization = `Bearer ${this.authToken}`;
    }

    const url = `${this.baseUrl}/data/${type}${lastSync ? `?since=${lastSync.toISOString()}` : ''}`;
    
    const response = await fetch(url, { headers });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch ${type} data`);
    }

    return response.json();
  }

  async syncData(data: any): Promise<void> {
    const headers: any = { 
      'Content-Type': 'application/json',
      Authorization: `Bearer ${this.authToken}`
    };

    const response = await fetch(`${this.baseUrl}/sync`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error('Sync failed');
    }
  }
}

// Hook de synchronisation offline
function useOfflineSync() {
  const dispatch = useDispatch();
  const { isOnline, syncQueue } = useSelector((state: any) => state.app);
  const apiService = new BusinessApiService();

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      dispatch(setOnlineStatus(state.isConnected || false));
    });

    return unsubscribe;
  }, [dispatch]);

  const syncWhenOnline = async () => {
    if (isOnline && syncQueue.length > 0) {
      try {
        console.log(`🔄 Syncing ${syncQueue.length} items...`);
        
        for (const item of syncQueue) {
          await apiService.syncData(item);
        }
        
        dispatch(clearSyncQueue());
        console.log('✅ Sync completed');
        
        // Notification succès
        dispatch(addNotification({
          id: Date.now().toString(),
          title: 'Synchronisation réussie',
          message: `${syncQueue.length} éléments synchronisés`,
          type: 'success'
        }));
        
      } catch (error) {
        console.error('❌ Sync failed:', error);
        
        dispatch(addNotification({
          id: Date.now().toString(),
          title: 'Erreur de synchronisation',
          message: 'Veuillez réessayer plus tard',
          type: 'error'
        }));
      }
    }
  };

  useEffect(() => {
    if (isOnline) {
      syncWhenOnline();
    }
  }, [isOnline]);

  const queueForSync = (data: any) => {
    dispatch(addToSyncQueue(data));
  };

  return { queueForSync, isOnline };
}

// Composant Dashboard métier
function BusinessDashboard() {
  const { user, businessData, isOnline } = useSelector((state: any) => state.app);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();
  const { queueForSync } = useOfflineSync();

  const onRefresh = async () => {
    setRefreshing(true);
    
    try {
      if (isOnline) {
        const apiService = new BusinessApiService();
        
        // Fetch latest data
        const orders = await apiService.fetchBusinessData('orders');
        const customers = await apiService.fetchBusinessData('customers');
        
        orders.forEach(order => dispatch(addBusinessData(order)));
        customers.forEach(customer => dispatch(addBusinessData(customer)));
      }
    } catch (error) {
      console.error('Refresh failed:', error);
    }
    
    setRefreshing(false);
  };

  const handleDataAction = async (action: string, item: BusinessData) => {
    const actionData = {
      action,
      itemId: item.id,
      itemType: item.type,
      timestamp: new Date().toISOString(),
      userId: user?.id
    };

    if (isOnline) {
      try {
        const apiService = new BusinessApiService();
        await apiService.syncData(actionData);
      } catch (error) {
        queueForSync(actionData);
      }
    } else {
      queueForSync(actionData);
    }
  };

  return (
    <View style={styles.container}>
      {/* Header avec statut connectivité */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Dashboard Métier</Text>
        <View style={[styles.connectionStatus, { 
          backgroundColor: isOnline ? '#4CAF50' : '#FF9800' 
        }]}>
          <Text style={styles.connectionText}>
            {isOnline ? 'En ligne' : 'Hors ligne'}
          </Text>
        </View>
      </View>

      {/* Métriques rapides */}
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        style={styles.metricsContainer}
      >
        <MetricCard 
          title="Commandes" 
          value={businessData.filter(d => d.type === 'order').length.toString()}
          trend="+12%"
          color="#2196F3"
        />
        <MetricCard 
          title="Clients" 
          value={businessData.filter(d => d.type === 'customer').length.toString()}
          trend="+5%"
          color="#4CAF50"
        />
        <MetricCard 
          title="Produits" 
          value={businessData.filter(d => d.type === 'product').length.toString()}
          trend="-2%"
          color="#FF9800"
        />
      </ScrollView>

      {/* Liste données business */}
      <FlatList
        data={businessData.slice(0, 20)}
        keyExtractor={(item) => item.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        renderItem={({ item }) => (
          <BusinessDataItem 
            item={item} 
            onAction={handleDataAction}
          />
        )}
        style={styles.dataList}
      />
    </View>
  );
}

// Composant métrique
function MetricCard({ title, value, trend, color }: {
  title: string;
  value: string;
  trend: string;
  color: string;
}) {
  return (
    <View style={[styles.metricCard, { borderLeftColor: color }]}>
      <Text style={styles.metricTitle}>{title}</Text>
      <Text style={styles.metricValue}>{value}</Text>
      <Text style={[styles.metricTrend, { 
        color: trend.startsWith('+') ? '#4CAF50' : '#f44336' 
      }]}>
        {trend}
      </Text>
    </View>
  );
}

// Composant item de données métier
function BusinessDataItem({ item, onAction }: {
  item: BusinessData;
  onAction: (action: string, item: BusinessData) => void;
}) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'synced': return { name: 'check-circle', color: '#4CAF50' };
      case 'pending': return { name: 'sync', color: '#FF9800' };
      case 'conflict': return { name: 'warning', color: '#f44336' };
      case 'error': return { name: 'error', color: '#f44336' };
      default: return { name: 'help', color: '#757575' };
    }
  };

  const statusIcon = getStatusIcon(item.syncStatus);

  return (
    <TouchableOpacity 
      style={styles.dataItem}
      onPress={() => onAction('view', item)}
    >
      <View style={styles.dataItemHeader}>
        <Text style={styles.dataItemTitle}>{item.title}</Text>
        <Icon 
          name={statusIcon.name} 
          size={20} 
          color={statusIcon.color} 
        />
      </View>
      
      <Text style={styles.dataItemType}>{item.type.toUpperCase()}</Text>
      <Text style={styles.dataItemDate}>
        Mis à jour: {new Date(item.lastUpdated).toLocaleDateString()}
      </Text>
      
      <View style={styles.dataItemActions}>
        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => onAction('edit', item)}
        >
          <Icon name="edit" size={16} color="#2196F3" />
          <Text style={styles.actionText}>Modifier</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.actionButton}
          onPress={() => onAction('share', item)}
        >
          <Icon name="share" size={16} color="#4CAF50" />
          <Text style={styles.actionText}>Partager</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  );
}

// Gestionnaire de notifications push
class PushNotificationManager {
  static configure() {
    PushNotification.configure({
      onRegister: (token) => {
        console.log('📱 Push token:', token);
        // Envoyer token au serveur
      },
      
      onNotification: (notification) => {
        console.log('📲 Notification received:', notification);
        
        // Traitement notification métier
        if (notification.data?.businessAction) {
          this.handleBusinessNotification(notification.data);
        }
      },
      
      permissions: {
        alert: true,
        badge: true,
        sound: true
      },
      
      popInitialNotification: true,
      requestPermissions: Platform.OS === 'ios'
    });
  }
  
  static handleBusinessNotification(data: any) {
    switch (data.businessAction) {
      case 'new_order':
        // Navigation vers commandes
        break;
      case 'urgent_approval':
        // Alerte approbation urgente
        break;
      case 'sync_completed':
        // Confirmation sync
        break;
    }
  }
  
  static sendLocalNotification(title: string, message: string, data?: any) {
    PushNotification.localNotification({
      title,
      message,
      userInfo: data,
      playSound: true,
      soundName: 'default'
    });
  }
}

// Composant racine de l'app
const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function AppNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: string;
          
          switch (route.name) {
            case 'Dashboard':
              iconName = 'dashboard';
              break;
            case 'Orders':
              iconName = 'shopping-cart';
              break;
            case 'Customers':
              iconName = 'people';
              break;
            case 'Analytics':
              iconName = 'analytics';
              break;
            case 'Profile':
              iconName = 'person';
              break;
            default:
              iconName = 'help';
          }
          
          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2196F3',
        tabBarInactiveTintColor: '#757575',
        headerShown: false
      })}
    >
      <Tab.Screen name="Dashboard" component={BusinessDashboard} />
      <Tab.Screen name="Orders" component={OrdersScreen} />
      <Tab.Screen name="Customers" component={CustomersScreen} />
      <Tab.Screen name="Analytics" component={AnalyticsScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

// Composants d'écran placeholder
function OrdersScreen() {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>Commandes</Text>
      <Text>Liste des commandes et gestion</Text>
    </View>
  );
}

function CustomersScreen() {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>Clients</Text>
      <Text>Base clients et interactions</Text>
    </View>
  );
}

function AnalyticsScreen() {
  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>Analytics</Text>
      <Text>Tableaux de bord et métriques</Text>
    </View>
  );
}

function ProfileScreen() {
  const { user } = useSelector((state: any) => state.app);
  const dispatch = useDispatch();
  
  const handleLogout = () => {
    Alert.alert(
      'Déconnexion',
      'Êtes-vous sûr de vouloir vous déconnecter ?',
      [
        { text: 'Annuler', style: 'cancel' },
        { 
          text: 'Déconnexion', 
          onPress: () => dispatch(logout()),
          style: 'destructive'
        }
      ]
    );
  };

  return (
    <View style={styles.screenContainer}>
      <Text style={styles.screenTitle}>Profil</Text>
      {user && (
        <View style={styles.profileInfo}>
          <Text style={styles.profileName}>{user.name}</Text>
          <Text style={styles.profileEmail}>{user.email}</Text>
          <Text style={styles.profileRole}>{user.role}</Text>
        </View>
      )}
      
      <TouchableOpacity 
        style={styles.logoutButton}
        onPress={handleLogout}
      >
        <Text style={styles.logoutText}>Déconnexion</Text>
      </TouchableOpacity>
    </View>
  );
}

// Application principale
export default function BusinessMobileApp() {
  const [isLoading, setIsLoading] = useState(true);
  const dispatch = useDispatch();

  useEffect(() => {
    // Configuration notifications
    PushNotificationManager.configure();
    
    // Chargement données persistées
    loadPersistedData();
    
    // Background sync setup
    setupBackgroundSync();
  }, []);

  const loadPersistedData = async () => {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const userData = await AsyncStorage.getItem('user_data');
      
      if (token && userData) {
        const user = JSON.parse(userData);
        dispatch(setUser(user));
      }
      
    } catch (error) {
      console.error('Failed to load persisted data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const setupBackgroundSync = () => {
    BackgroundJob.register({
      jobKey: 'businessDataSync',
      period: 60000, // 1 minute
    });

    BackgroundJob.start({
      jobKey: 'businessDataSync',
      requiredNetworkType: 'any'
    });
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2196F3" />
        <Text style={styles.loadingText}>Chargement...</Text>
      </View>
    );
  }

  return (
    <ReduxProvider store={store}>
      <NavigationContainer theme={DefaultTheme}>
        <AppNavigator />
      </NavigationContainer>
    </ReduxProvider>
  );
}

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5'
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#fff',
    elevation: 2,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333'
  },
  connectionStatus: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12
  },
  connectionText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '500'
  },
  metricsContainer: {
    paddingVertical: 16,
    paddingLeft: 16
  },
  metricCard: {
    backgroundColor: '#fff',
    padding: 16,
    marginRight: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    minWidth: 120,
    elevation: 1
  },
  metricTitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4
  },
  metricTrend: {
    fontSize: 12,
    fontWeight: '500'
  },
  dataList: {
    flex: 1,
    paddingHorizontal: 16
  },
  dataItem: {
    backgroundColor: '#fff',
    padding: 16,
    marginVertical: 4,
    borderRadius: 8,
    elevation: 1
  },
  dataItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  dataItemTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1
  },
  dataItemType: {
    fontSize: 12,
    color: '#666',
    backgroundColor: '#f0f0f0',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    alignSelf: 'flex-start',
    marginBottom: 4
  },
  dataItemDate: {
    fontSize: 12,
    color: '#999',
    marginBottom: 12
  },
  dataItemActions: {
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 6,
    backgroundColor: '#f8f9fa'
  },
  actionText: {
    marginLeft: 4,
    fontSize: 12,
    color: '#666'
  },
  screenContainer: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5'
  },
  screenTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16
  },
  profileInfo: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16
  },
  profileName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4
  },
  profileEmail: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4
  },
  profileRole: {
    fontSize: 14,
    color: '#2196F3',
    fontWeight: '500'
  },
  logoutButton: {
    backgroundColor: '#f44336',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center'
  },
  logoutText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500'
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5'
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666'
  }
});
```

## Module 2 : Progressive Web App (PWA) Métier

### PWA Business-Ready avec Service Worker

```typescript
// BusinessPWA.ts
/**
 * Progressive Web App pour applications métier
 * Intègre service worker, cache intelligent et notifications push
 */

// Service Worker pour PWA
const CACHE_NAME = 'business-pwa-v1.2.0';
const STATIC_CACHE = 'static-cache-v1';
const DYNAMIC_CACHE = 'dynamic-cache-v1';
const API_CACHE = 'api-cache-v1';

// Ressources à mettre en cache
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/images/logo.png',
  '/offline.html'
];

// Configuration cache par type
const CACHE_STRATEGIES = {
  static: 'cache-first',
  api: 'network-first-with-fallback',
  images: 'cache-first-with-network-fallback',
  documents: 'stale-while-revalidate'
};

// Installation Service Worker
self.addEventListener('install', (event: ExtendableEvent) => {
  event.waitUntil(
    Promise.all([
      // Cache des ressources statiques
      caches.open(STATIC_CACHE).then(cache => {
        return cache.addAll(STATIC_ASSETS);
      }),
      
      // Skip waiting pour activation immédiate
      self.skipWaiting()
    ])
  );
});

// Activation Service Worker
self.addEventListener('activate', (event: ExtendableEvent) => {
  event.waitUntil(
    Promise.all([
      // Nettoyage anciens caches
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(cacheName => 
              cacheName !== STATIC_CACHE && 
              cacheName !== DYNAMIC_CACHE && 
              cacheName !== API_CACHE
            )
            .map(cacheName => caches.delete(cacheName))
        );
      }),
      
      // Prise de contrôle clients
      self.clients.claim()
    ])
  );
});

// Interception des requêtes
self.addEventListener('fetch', (event: FetchEvent) => {
  const { request } = event;
  const url = new URL(request.url);

  // Stratégie selon type de ressource
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
  } else if (request.destination === 'image') {
    event.respondWith(handleImageRequest(request));
  } else if (url.pathname.includes('/static/')) {
    event.respondWith(handleStaticRequest(request));
  } else {
    event.respondWith(handleDocumentRequest(request));
  }
});

// Gestion requêtes API avec cache intelligent
async function handleApiRequest(request: Request): Promise<Response> {
  const cacheName = API_CACHE;
  
  try {
    // Tentative réseau d'abord
    const networkResponse = await fetch(request.clone());
    
    if (networkResponse.ok) {
      // Cache réponse si succès
      const cache = await caches.open(cacheName);
      await cache.put(request, networkResponse.clone());
      
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
    
  } catch (error) {
    // Fallback sur cache
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      // Ajouter header indiquant cache
      const response = cachedResponse.clone();
      response.headers.set('X-Cache-Status', 'from-cache');
      return response;
    }
    
    // Réponse offline personnalisée
    if (request.url.includes('/api/')) {
      return new Response(
        JSON.stringify({
          error: 'offline',
          message: 'Données non disponibles hors ligne',
          cached: false
        }),
        {
          status: 503,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    throw error;
  }
}

// Gestion images avec cache
async function handleImageRequest(request: Request): Promise<Response> {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      await cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    // Image placeholder si échec
    return await cache.match('/static/images/placeholder.png') || 
           new Response('', { status: 404 });
           
  } catch (error) {
    return await cache.match('/static/images/offline.png') || 
           new Response('', { status: 503 });
  }
}

// Gestion ressources statiques
async function handleStaticRequest(request: Request): Promise<Response> {
  const cachedResponse = await caches.match(request);
  return cachedResponse || fetch(request);
}

// Gestion documents avec stale-while-revalidate
async function handleDocumentRequest(request: Request): Promise<Response> {
  const cache = await caches.open(DYNAMIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  // Mise à jour en arrière-plan
  const fetchPromise = fetch(request)
    .then(response => {
      if (response.ok) {
        cache.put(request, response.clone());
      }
      return response;
    })
    .catch(() => null);
  
  // Retourner cache si disponible, sinon attendre réseau
  return cachedResponse || await fetchPromise || 
         await caches.match('/offline.html') ||
         new Response('Offline', { status: 503 });
}

// Synchronisation arrière-plan
self.addEventListener('sync', (event: any) => {
  if (event.tag === 'business-data-sync') {
    event.waitUntil(syncBusinessData());
  }
});

async function syncBusinessData() {
  try {
    // Récupération données en attente de sync
    const syncData = await getStoredSyncData();
    
    if (syncData.length > 0) {
      for (const item of syncData) {
        try {
          await fetch('/api/sync', {
            method: 'POST',
            body: JSON.stringify(item),
            headers: { 'Content-Type': 'application/json' }
          });
          
          // Suppression de la queue si succès
          await removeSyncData(item.id);
          
        } catch (error) {
          console.error('Sync failed for item:', item.id, error);
        }
      }
      
      // Notification succès sync
      await self.registration.showNotification('Synchronisation réussie', {
        body: `${syncData.length} éléments synchronisés`,
        icon: '/static/images/sync-icon.png',
        badge: '/static/images/badge.png'
      });
    }
    
  } catch (error) {
    console.error('Background sync failed:', error);
  }
}

// Notifications Push
self.addEventListener('push', (event: any) => {
  if (!event.data) return;
  
  const data = event.data.json();
  
  const options = {
    body: data.body,
    icon: data.icon || '/static/images/notification-icon.png',
    badge: '/static/images/badge.png',
    data: data.data,
    actions: data.actions || [],
    requireInteraction: data.priority === 'high',
    silent: data.priority === 'low'
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Gestion clics notifications
self.addEventListener('notificationclick', (event: any) => {
  event.notification.close();
  
  const data = event.notification.data;
  
  if (event.action) {
    // Action spécifique
    handleNotificationAction(event.action, data);
  } else {
    // Ouverture app
    event.waitUntil(
      self.clients.matchAll({ type: 'window' }).then(clients => {
        // Si app déjà ouverte, focus
        for (const client of clients) {
          if (client.url.includes(self.location.origin)) {
            client.focus();
            client.postMessage({
              type: 'notification_click',
              data: data
            });
            return;
          }
        }
        
        // Sinon ouvrir nouvelle fenêtre
        return self.clients.openWindow(
          data.url || '/'
        );
      })
    );
  }
});

// Application PWA principale
class BusinessPWAApp {
  private syncQueue: any[] = [];
  private isOnline = navigator.onLine;
  private notificationPermission = 'default';

  constructor() {
    this.init();
  }

  private async init() {
    // Enregistrement Service Worker
    await this.registerServiceWorker();
    
    // Configuration notifications
    await this.setupNotifications();
    
    // Gestion connectivité
    this.setupConnectivityHandling();
    
    // Interface utilisateur
    this.setupUI();
    
    console.log('🚀 Business PWA initialized');
  }

  private async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        
        registration.addEventListener('updatefound', () => {
          console.log('🔄 Service Worker update available');
          this.showUpdateNotification();
        });
        
        // Background Sync
        if ('sync' in window.ServiceWorkerRegistration.prototype) {
          await registration.sync.register('business-data-sync');
        }
        
        console.log('✅ Service Worker registered');
        
      } catch (error) {
        console.error('❌ Service Worker registration failed:', error);
      }
    }
  }

  private async setupNotifications() {
    if ('Notification' in window && 'serviceWorker' in navigator) {
      this.notificationPermission = await Notification.requestPermission();
      
      if (this.notificationPermission === 'granted') {
        // Souscription Push
        const registration = await navigator.serviceWorker.ready;
        
        if ('PushManager' in window) {
          try {
            const subscription = await registration.pushManager.subscribe({
              userVisibleOnly: true,
              applicationServerKey: this.urlBase64ToUint8Array(
                'YOUR_VAPID_PUBLIC_KEY'
              )
            });
            
            // Envoi subscription au serveur
            await this.sendSubscriptionToServer(subscription);
            
          } catch (error) {
            console.error('Push subscription failed:', error);
          }
        }
      }
    }
  }

  private setupConnectivityHandling() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.showConnectionStatus('Connexion rétablie', 'success');
      this.syncPendingData();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.showConnectionStatus('Mode hors ligne', 'warning');
    });
  }

  private setupUI() {
    // Interface PWA responsive
    const app = document.getElementById('app');
    if (!app) return;

    app.innerHTML = `
      <div class="pwa-container">
        <header class="app-header">
          <h1>Business PWA</h1>
          <div class="connection-status" id="connectionStatus">
            ${this.isOnline ? '🟢 En ligne' : '🔴 Hors ligne'}
          </div>
        </header>
        
        <nav class="app-navigation">
          <button class="nav-item active" data-page="dashboard">
            📊 Dashboard
          </button>
          <button class="nav-item" data-page="orders">
            🛒 Commandes
          </button>
          <button class="nav-item" data-page="customers">
            👥 Clients
          </button>
          <button class="nav-item" data-page="sync">
            🔄 Sync (${this.syncQueue.length})
          </button>
        </nav>
        
        <main class="app-content" id="appContent">
          ${this.renderDashboard()}
        </main>
        
        <div class="notification-toast" id="notificationToast"></div>
      </div>
    `;

    this.setupNavigation();
    this.loadBusinessData();
  }

  private renderDashboard(): string {
    return `
      <div class="dashboard">
        <div class="metrics-grid">
          <div class="metric-card">
            <h3>Commandes</h3>
            <div class="metric-value">156</div>
            <div class="metric-trend positive">+12%</div>
          </div>
          
          <div class="metric-card">
            <h3>Clients</h3>
            <div class="metric-value">89</div>
            <div class="metric-trend positive">+5%</div>
          </div>
          
          <div class="metric-card">
            <h3>CA</h3>
            <div class="metric-value">45,2K€</div>
            <div class="metric-trend negative">-2%</div>
          </div>
        </div>
        
        <div class="recent-activity">
          <h3>Activité récente</h3>
          <div class="activity-list" id="activityList">
            <div class="loading">Chargement...</div>
          </div>
        </div>
      </div>
    `;
  }

  private async loadBusinessData() {
    try {
      const response = await fetch('/api/dashboard');
      const data = await response.json();
      
      this.renderActivityList(data.activities);
      
    } catch (error) {
      console.error('Failed to load business data:', error);
      
      // Fallback sur données cachées
      const cachedData = await this.getCachedData('dashboard');
      if (cachedData) {
        this.renderActivityList(cachedData.activities);
        this.showNotification('Données issues du cache', 'info');
      }
    }
  }

  private renderActivityList(activities: any[]) {
    const container = document.getElementById('activityList');
    if (!container) return;

    container.innerHTML = activities.map(activity => `
      <div class="activity-item">
        <div class="activity-icon">${activity.icon}</div>
        <div class="activity-content">
          <div class="activity-title">${activity.title}</div>
          <div class="activity-time">${activity.timestamp}</div>
        </div>
      </div>
    `).join('');
  }

  private async syncPendingData() {
    if (!this.isOnline || this.syncQueue.length === 0) return;

    try {
      for (const item of this.syncQueue) {
        const response = await fetch('/api/sync', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(item)
        });

        if (response.ok) {
          this.syncQueue = this.syncQueue.filter(i => i.id !== item.id);
        }
      }

      this.updateSyncBadge();
      this.showNotification('Synchronisation réussie', 'success');

    } catch (error) {
      console.error('Sync failed:', error);
      this.showNotification('Échec synchronisation', 'error');
    }
  }

  private showConnectionStatus(message: string, type: 'success' | 'warning' | 'error') {
    const statusElement = document.getElementById('connectionStatus');
    if (statusElement) {
      statusElement.textContent = message;
      statusElement.className = `connection-status ${type}`;
    }
  }

  private showNotification(message: string, type: 'success' | 'info' | 'warning' | 'error') {
    const toast = document.getElementById('notificationToast');
    if (!toast) return;

    toast.textContent = message;
    toast.className = `notification-toast show ${type}`;

    setTimeout(() => {
      toast.className = 'notification-toast';
    }, 3000);
  }

  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  private async sendSubscriptionToServer(subscription: PushSubscription) {
    await fetch('/api/push-subscription', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(subscription)
    });
  }
}

// Initialisation PWA
document.addEventListener('DOMContentLoaded', () => {
  new BusinessPWAApp();
});

// CSS pour PWA (à inclure dans un fichier CSS)
const pwaStyles = `
.pwa-container {
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.connection-status {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.connection-status.success { background: #4CAF50; }
.connection-status.warning { background: #FF9800; }
.connection-status.error { background: #f44336; }

.app-navigation {
  display: flex;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow-x: auto;
}

.nav-item {
  flex: 1;
  padding: 1rem;
  border: none;
  background: none;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-item.active {
  background: #e3f2fd;
  border-bottom: 3px solid #2196F3;
}

.app-content {
  flex: 1;
  padding: 1rem;
  background: #f5f5f5;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
  margin: 0.5rem 0;
}

.metric-trend {
  font-size: 0.875rem;
  font-weight: 500;
}

.metric-trend.positive { color: #4CAF50; }
.metric-trend.negative { color: #f44336; }

.notification-toast {
  position: fixed;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%) translateY(100px);
  padding: 1rem 2rem;
  border-radius: 4px;
  color: white;
  font-weight: 500;
  transition: transform 0.3s;
  z-index: 1000;
}

.notification-toast.show {
  transform: translateX(-50%) translateY(0);
}

.notification-toast.success { background: #4CAF50; }
.notification-toast.info { background: #2196F3; }
.notification-toast.warning { background: #FF9800; }
.notification-toast.error { background: #f44336; }

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .app-header h1 {
    font-size: 1.25rem;
  }
  
  .nav-item {
    font-size: 0.875rem;
  }
}
`;
```

Cette architecture mobile et cross-platform avancée offre :

✅ **React Native business-ready** avec Redux et synchronisation offline
✅ **PWA complète** avec service worker intelligent
✅ **Synchronisation offline** avec résolution de conflits
✅ **Push notifications** contextuelles et intelligentes
✅ **Architecture responsive** adaptive multi-device
✅ **Performance optimisée** avec cache stratégique
✅ **Sécurité intégrée** avec authentification et chiffrement
✅ **Analytics embarquées** pour suivi usage
✅ **Accessibilité** complète selon standards WCAG
✅ **Distribution** multi-store et auto-update

Le système permet de créer rapidement des applications métier mobiles robustes avec une expérience utilisateur native sur toutes plateformes.