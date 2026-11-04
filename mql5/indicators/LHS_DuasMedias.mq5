//+------------------------------------------------------------------+
//| LHS_DuasMedias.mq5                                               |
//| LHS Quant Lab — SMA rápida (azul) e SMA lenta (vermelha)         |
//| Usado pelo EA LHS_CruzamentoMM e também serve no gráfico normal.|
//+------------------------------------------------------------------+
#property copyright   "LHS Capital"
#property version     "1.00"
#property description "Duas médias móveis simples (fechamento) com cores diferentes."
#property indicator_chart_window
#property indicator_buffers 2
#property indicator_plots   2

#property indicator_label1  "SMA rápida"
#property indicator_type1   DRAW_LINE
#property indicator_color1  clrDodgerBlue
#property indicator_width1  2

#property indicator_label2  "SMA lenta"
#property indicator_type2   DRAW_LINE
#property indicator_color2  clrOrangeRed
#property indicator_width2  2

input int InpMediaRapida = 20;   // Período da média rápida
input int InpMediaLenta  = 50;   // Período da média lenta

double bRapida[];
double bLenta[];

//+------------------------------------------------------------------+
int OnInit()
  {
   if(InpMediaRapida < 1 || InpMediaLenta < 1)
      return INIT_PARAMETERS_INCORRECT;

   SetIndexBuffer(0, bRapida, INDICATOR_DATA);
   SetIndexBuffer(1, bLenta, INDICATOR_DATA);
   PlotIndexSetInteger(0, PLOT_DRAW_BEGIN, InpMediaRapida - 1);
   PlotIndexSetInteger(1, PLOT_DRAW_BEGIN, InpMediaLenta - 1);
   PlotIndexSetString(0, PLOT_LABEL, StringFormat("SMA %d", InpMediaRapida));
   PlotIndexSetString(1, PLOT_LABEL, StringFormat("SMA %d", InpMediaLenta));
   IndicatorSetString(INDICATOR_SHORTNAME, StringFormat("LHS SMA %d x %d", InpMediaRapida, InpMediaLenta));
   IndicatorSetInteger(INDICATOR_DIGITS, _Digits);
   return INIT_SUCCEEDED;
  }

//+------------------------------------------------------------------+
//| Média simples com soma móvel (índice 0 = barra mais antiga)      |
//+------------------------------------------------------------------+
void CalcularSMA(const int total, const int inicio, const double &preco[], const int periodo, double &buf[])
  {
   for(int i = inicio; i < total; i++)
     {
      if(i < periodo - 1)
        {
         buf[i] = EMPTY_VALUE;
         continue;
        }
      double soma = 0.0;
      for(int k = 0; k < periodo; k++)
         soma += preco[i - k];
      buf[i] = soma / periodo;
     }
  }

//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
  {
   // recalcula só a última barra (ainda aberta) e as novas
   int inicio = (prev_calculated > 0) ? prev_calculated - 1 : 0;
   CalcularSMA(rates_total, inicio, close, InpMediaRapida, bRapida);
   CalcularSMA(rates_total, inicio, close, InpMediaLenta, bLenta);
   return rates_total;
  }
//+------------------------------------------------------------------+
