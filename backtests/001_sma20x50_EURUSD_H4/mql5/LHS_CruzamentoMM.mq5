//+------------------------------------------------------------------+
//| LHS_CruzamentoMM.mq5                                             |
//| LHS Quant Lab — réplica do notebook 02_primeiro_backtest         |
//|                                                                  |
//| Regra: SMA rápida > SMA lenta  -> comprado                       |
//|        SMA rápida < SMA lenta  -> vendido                        |
//|        sempre posicionado; no cruzamento, zera e vira a mão.     |
//| Sem look-ahead: decide com a barra JÁ FECHADA (índice 1) e       |
//| executa no primeiro tick da barra seguinte.                      |
//|                                                                  |
//| Segurança: no Testador de Estratégia opera livremente (dinheiro  |
//| simulado). Fora do testador só roda em conta DEMO e com          |
//| InpPermitirOrdens = true.                                        |
//+------------------------------------------------------------------+
#property copyright   "LHS Capital"
#property version     "1.00"
#property description "Cruzamento de médias SMA rápida x lenta, sempre posicionado (stop and reverse)."
#property description "Feito para o Testador de Estratégia em modo visual."
#property description "Fora do testador: só conta DEMO e com InpPermitirOrdens = true."
#property tester_indicator "LHSQuantLab\\LHS_DuasMedias.ex5"

#include <Trade\Trade.mqh>

input group "Estratégia"
input int    InpMediaRapida    = 20;        // Período da média rápida
input int    InpMediaLenta     = 50;        // Período da média lenta

input group "Tamanho da posição"
input bool   InpLoteAuto       = true;      // Lote automático = exposição de 1x o capital (igual ao notebook)
input double InpLoteFixo       = 0.10;      // Lote fixo (se o automático estiver desligado)

input group "Execução"
input int    InpDesvioPontos   = 2;         // Desvio (slippage) máximo aceito, em pontos
input ulong  InpMagic          = 20261017;  // Número mágico das ordens desta EA

input group "Segurança"
input bool   InpPermitirOrdens = false;     // Fora do testador: liberar ordens (só conta DEMO)

CTrade   trade;
int      hMedias      = INVALID_HANDLE;
datetime ultimaBarra  = 0;
int      nOperacoes   = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpMediaRapida >= InpMediaLenta)
     {
      Print("A média rápida precisa ser menor que a lenta.");
      return INIT_PARAMETERS_INCORRECT;
     }

   // trava de segurança fora do testador
   if(!MQLInfoInteger(MQL_TESTER))
     {
      if(AccountInfoInteger(ACCOUNT_TRADE_MODE) != ACCOUNT_TRADE_MODE_DEMO)
        {
         Alert("LHS_CruzamentoMM: esta conta NÃO é demo. EA bloqueada.");
         return INIT_FAILED;
        }
      if(!InpPermitirOrdens)
        {
         Alert("LHS_CruzamentoMM: InpPermitirOrdens = false. Ligue nos parâmetros para operar na demo.");
         return INIT_FAILED;
        }
     }

   hMedias = iCustom(_Symbol, _Period, "LHSQuantLab\\LHS_DuasMedias", InpMediaRapida, InpMediaLenta);
   if(hMedias == INVALID_HANDLE)
     {
      Print("Não consegui carregar o indicador LHSQuantLab\\LHS_DuasMedias. Erro ", GetLastError());
      return INIT_FAILED;
     }
   ChartIndicatorAdd(0, 0, hMedias);   // mostra as médias no gráfico (azul = rápida, vermelha = lenta)

   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpDesvioPontos);
   trade.SetTypeFillingBySymbol(_Symbol);
   return INIT_SUCCEEDED;
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(hMedias != INVALID_HANDLE)
      IndicatorRelease(hMedias);
   Comment("");
  }

//+------------------------------------------------------------------+
//| Posição atual desta EA: +1 comprado, -1 vendido, 0 fora          |
//+------------------------------------------------------------------+
int PosicaoAtual(ulong &ticket)
  {
   ticket = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong t = PositionGetTicket(i);
      if(PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != (long)InpMagic)
         continue;
      ticket = t;
      return (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? 1 : -1;
     }
   return 0;
  }

//+------------------------------------------------------------------+
//| Lote: fixo ou 1x o capital (valor nocional = patrimônio)         |
//+------------------------------------------------------------------+
double CalcularLote()
  {
   double lote = InpLoteFixo;
   if(InpLoteAuto)
     {
      double contrato = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
      double preco    = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      if(contrato > 0 && preco > 0)
         lote = AccountInfoDouble(ACCOUNT_EQUITY) / (contrato * preco);
     }
   double passo  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double minimo = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maximo = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   lote = MathFloor(lote / passo) * passo;
   return NormalizeDouble(MathMax(minimo, MathMin(maximo, lote)), 2);
  }

//+------------------------------------------------------------------+
void AtualizarPainel(const int pos, const double rapida, const double lenta)
  {
   string estado = (pos == 1) ? "COMPRADO" : (pos == -1) ? "VENDIDO" : "FORA";
   double saldo  = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   Comment(StringFormat("LHS Quant Lab — Cruzamento SMA %d x %d  (%s %s)\n"
                        "SMA rápida (azul): %s   |   SMA lenta (vermelha): %s\n"
                        "Posição: %s   |   Operações: %d\n"
                        "Saldo: %.2f   |   Patrimônio: %.2f",
                        InpMediaRapida, InpMediaLenta, _Symbol, EnumToString(_Period),
                        DoubleToString(rapida, _Digits), DoubleToString(lenta, _Digits),
                        estado, nOperacoes, saldo, equity));
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   // só age uma vez por barra, no primeiro tick da barra nova
   datetime barra = iTime(_Symbol, _Period, 0);
   if(barra == ultimaBarra)
      return;

   double rapida[1], lenta[1];
   if(CopyBuffer(hMedias, 0, 1, 1, rapida) != 1 || CopyBuffer(hMedias, 1, 1, 1, lenta) != 1)
      return;   // indicador ainda calculando: tenta no próximo tick
   ultimaBarra = barra;

   ulong ticket;
   int pos = PosicaoAtual(ticket);
   if(rapida[0] == EMPTY_VALUE || lenta[0] == EMPTY_VALUE)
     {
      AtualizarPainel(pos, 0, 0);
      return;   // ainda não há barras suficientes para a média lenta
     }

   // sinal da barra fechada
   int desejada = (rapida[0] > lenta[0]) ? 1 : -1;

   if(pos != desejada)
     {
      if(pos != 0 && !trade.PositionClose(ticket))
        {
         Print("Falha ao fechar posição: ", trade.ResultRetcodeDescription());
         ultimaBarra = 0;   // tenta de novo no próximo tick
         return;
        }
      double lote = CalcularLote();
      bool ok = (desejada == 1) ? trade.Buy(lote, _Symbol, 0, 0, 0, "LHS SMA compra")
                                : trade.Sell(lote, _Symbol, 0, 0, 0, "LHS SMA venda");
      if(ok)
        {
         nOperacoes++;
         pos = desejada;
        }
      else
        {
         Print("Falha ao abrir posição: ", trade.ResultRetcodeDescription());
         ultimaBarra = 0;
        }
     }
   AtualizarPainel(pos, rapida[0], lenta[0]);
  }
//+------------------------------------------------------------------+
